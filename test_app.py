import unittest
import json
from datetime import datetime, timezone
from app import app, db, Transaction, Budget, Goal

class PersonalFinanceAdvisorBotTests(unittest.TestCase):

    def setUp(self):
        # Configure app for testing with an in-memory database
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_dashboard_empty_renders_properly(self):
        """Dashboard renders successfully with 0 records without template errors."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Personal Finance Advisor Bot", response.data)
        self.assertIn(b"No transactions recorded yet", response.data)

    def test_add_income_and_expense_transactions(self):
        """Test adding both income and expense transactions."""
        # Add income
        resp_income = self.client.post("/transactions/add", data={
            "kind": "income",
            "category": "Salary",
            "amount": "50000",
            "date": "2026-09-01",
            "note": "September Tech Salary"
        }, follow_redirects=True)
        self.assertEqual(resp_income.status_code, 200)
        self.assertIn(b"Transaction recorded successfully!", resp_income.data)

        # Add expense
        resp_expense = self.client.post("/transactions/add", data={
            "kind": "expense",
            "category": "Food",
            "amount": "4500",
            "date": "2026-09-02",
            "note": "Groceries"
        }, follow_redirects=True)
        self.assertEqual(resp_expense.status_code, 200)

        with app.app_context():
            self.assertEqual(Transaction.query.count(), 2)
            income_t = Transaction.query.filter_by(kind="income").first()
            self.assertEqual(income_t.amount, 50000.0)
            self.assertEqual(income_t.category, "Salary")

    def test_invalid_transaction_amount_rejected(self):
        """Ensure non-positive amounts or invalid kind are rejected gracefully."""
        resp = self.client.post("/transactions/add", data={
            "kind": "expense",
            "category": "Food",
            "amount": "-500",
            "note": "Invalid negative"
        }, follow_redirects=True)
        self.assertIn(b"Error adding transaction", resp.data)

        with app.app_context():
            self.assertEqual(Transaction.query.count(), 0)

    def test_delete_transaction(self):
        """Test deleting an existing transaction."""
        with app.app_context():
            t = Transaction(kind="expense", category="Rent", amount=15000.0, note="Rent test")
            db.session.add(t)
            db.session.commit()
            tid = t.id

        del_resp = self.client.post(f"/transactions/{tid}/delete", follow_redirects=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertIn(b"Transaction deleted.", del_resp.data)

        with app.app_context():
            self.assertIsNone(db.session.get(Transaction, tid))

    def test_budget_create_update_and_delete(self):
        """Test creating, updating, and deleting category budgets."""
        # Create budget
        resp = self.client.post("/budgets/save", data={
            "category": "Food",
            "limit": "8000"
        }, follow_redirects=True)
        self.assertIn(b"Created budget for Food at \xe2\x82\xb98,000.", resp.data)

        with app.app_context():
            b = Budget.query.filter_by(category="Food").first()
            self.assertIsNotNone(b)
            self.assertEqual(b.limit, 8000.0)
            bid = b.id

        # Update budget
        resp_up = self.client.post("/budgets/save", data={
            "category": "Food",
            "limit": "9500"
        }, follow_redirects=True)
        self.assertIn(b"Updated budget for Food to \xe2\x82\xb99,500.", resp_up.data)

        # Delete budget
        resp_del = self.client.post(f"/budgets/{bid}/delete", follow_redirects=True)
        self.assertIn(b"Deleted budget for Food.", resp_del.data)

        with app.app_context():
            self.assertIsNone(db.session.get(Budget, bid))

    def test_goals_lifecycle(self):
        """Test creating a savings goal, depositing funds, completion, and deletion."""
        # Create goal
        resp = self.client.post("/goals/add", data={
            "name": "Emergency Fund",
            "target": "20000",
            "saved": "5000",
            "deadline": "2026-12-31"
        }, follow_redirects=True)
        self.assertIn(b"Emergency Fund", resp.data)
        self.assertIn(b"created", resp.data)

        with app.app_context():
            g = Goal.query.filter_by(name="Emergency Fund").first()
            self.assertIsNotNone(g)
            self.assertEqual(g.pct, 25.0)
            self.assertFalse(g.is_completed)
            gid = g.id

        # Add saving
        resp_add = self.client.post(f"/goals/{gid}/add", data={
            "amount": "15000"
        }, follow_redirects=True)
        self.assertIn(b"reached your goal", resp_add.data)
        self.assertIn(b"Emergency Fund", resp_add.data)

        with app.app_context():
            g_updated = db.session.get(Goal, gid)
            self.assertEqual(g_updated.saved, 20000.0)
            self.assertTrue(g_updated.is_completed)

        # Delete goal
        resp_del = self.client.post(f"/goals/{gid}/delete", follow_redirects=True)
        self.assertIn(b"Emergency Fund", resp_del.data)
        self.assertIn(b"removed", resp_del.data)

        with app.app_context():
            self.assertIsNone(db.session.get(Goal, gid))

    def test_reports_page(self):
        """Test reports page calculations and rendering."""
        with app.app_context():
            db.session.add(Transaction(kind="income", category="Salary", amount=60000.0))
            db.session.add(Transaction(kind="expense", category="Rent", amount=20000.0))
            db.session.add(Transaction(kind="expense", category="Food", amount=8000.0))
            db.session.add(Budget(category="Food", limit=10000.0))
            db.session.commit()

        resp = self.client.get("/reports")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Financial Reports", resp.data)
        self.assertIn(b"60000", resp.data)
        self.assertIn(b"28000", resp.data)

    def test_api_summary(self):
        """Test the /api/summary JSON endpoint."""
        with app.app_context():
            db.session.add(Transaction(kind="income", category="Salary", amount=50000.0))
            db.session.add(Transaction(kind="expense", category="Food", amount=5000.0))
            db.session.commit()

        resp = self.client.get("/api/summary")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["income"], 50000.0)
        self.assertEqual(data["expense"], 5000.0)
        self.assertEqual(data["balance"], 45000.0)
        self.assertEqual(data["savings_rate"], 90.0)

    def test_api_ai_advice(self):
        """Test /api/ai-advice endpoint returns structured advice."""
        resp = self.client.get("/api/ai-advice")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn("provider", data)
        self.assertIn("advice", data)
        self.assertIsInstance(data["advice"], list)
        self.assertTrue(len(data["advice"]) > 0)

    def test_api_ai_chat_conversational_queries(self):
        """Test the interactive AI Advisor Bot chat responses for multiple finance questions."""
        with app.app_context():
            db.session.add(Transaction(kind="income", category="Salary", amount=60000.0))
            db.session.add(Transaction(kind="expense", category="Food", amount=7000.0))
            db.session.add(Transaction(kind="expense", category="Rent", amount=20000.0))
            db.session.add(Budget(category="Food", limit=6000.0))  # Exceeded budget!
            db.session.add(Goal(name="Vacation", target=30000.0, saved=10000.0))
            db.session.commit()

        # 1. 50/30/20 rule
        r1 = self.client.post("/api/ai-chat", json={"message": "What is the 50/30/20 rule for my income?"})
        self.assertEqual(r1.status_code, 200)
        d1 = json.loads(r1.data)
        self.assertIn("50/30/20", d1["reply"])
        self.assertIn("Needs", d1["reply"])

        # 2. Saving money
        r2 = self.client.post("/api/ai-chat", json={"message": "How can I save more money?"})
        d2 = json.loads(r2.data)
        self.assertIn("Save", d2["reply"])

        # 3. Budget status
        r3 = self.client.post("/api/ai-chat", json={"message": "Check my budget status"})
        d3 = json.loads(r3.data)
        self.assertIn("Food", d3["reply"])
        self.assertIn("Budget", d3["reply"])

        # 4. Affordability question
        r4 = self.client.post("/api/ai-chat", json={"message": "Can I afford a ₹15,000 phone?"})
        d4 = json.loads(r4.data)
        self.assertIn("afford", d4["reply"].lower())

    def test_export_csv(self):
        """Test exporting transactions as CSV."""
        with app.app_context():
            db.session.add(Transaction(kind="income", category="Salary", amount=40000.0, note="Bonus"))
            db.session.commit()

        resp = self.client.get("/export/csv")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "text/csv")
        self.assertIn(b"Salary", resp.data)
        self.assertIn(b"40000.00", resp.data)

    def test_seed_demo_route(self):
        """Test the /seed-demo endpoint populates sample records."""
        resp = self.client.get("/seed-demo", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Demo data loaded successfully!", resp.data)

        with app.app_context():
            self.assertTrue(Transaction.query.count() >= 10)
            self.assertTrue(Budget.query.count() >= 4)
            self.assertTrue(Goal.query.count() >= 2)


if __name__ == "__main__":
    unittest.main()
