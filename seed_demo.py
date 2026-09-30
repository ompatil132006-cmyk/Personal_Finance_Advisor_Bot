"""
Seed demo data for Personal Finance Advisor Bot.
Can be executed directly: `py seed_demo.py`
or called from the web application `/seed-demo`.
"""
from datetime import datetime, timedelta, timezone

def seed_database(clear_existing=True):
    from app import app, db, Transaction, Budget, Goal

    with app.app_context():
        if clear_existing:
            Transaction.query.delete()
            Budget.query.delete()
            Goal.query.delete()
            db.session.commit()

        now = datetime.now(timezone.utc)

        # 1. Sample Transactions
        sample_transactions = [
            # Incomes
            {"kind": "income", "category": "Salary", "amount": 65000.0, "note": "Primary Tech Job Monthly Salary", "days_ago": 25},
            {"kind": "income", "category": "Freelance", "amount": 18500.0, "note": "Freelance UI/UX Project Milestone", "days_ago": 12},
            {"kind": "income", "category": "Investment", "amount": 3200.0, "note": "Quarterly Mutual Fund Dividend", "days_ago": 5},

            # Expenses
            {"kind": "expense", "category": "Rent", "amount": 22000.0, "note": "Monthly Apartment Rent Payment", "days_ago": 26},
            {"kind": "expense", "category": "Food", "amount": 5400.0, "note": "Supermarket Grocery Run", "days_ago": 22},
            {"kind": "expense", "category": "Utilities", "amount": 2800.0, "note": "Electricity & Water Bills", "days_ago": 20},
            {"kind": "expense", "category": "Transport", "amount": 2600.0, "note": "Metro Smart Card Recharge & Fuel", "days_ago": 18},
            {"kind": "expense", "category": "Entertainment", "amount": 3400.0, "note": "Weekend Dining & Cinema Tickets", "days_ago": 15},
            {"kind": "expense", "category": "Education", "amount": 2499.0, "note": "Data Science & AI Certification Course", "days_ago": 14},
            {"kind": "expense", "category": "Food", "amount": 2150.0, "note": "Mid-month Grocery & Fresh Produce", "days_ago": 10},
            {"kind": "expense", "category": "Healthcare", "amount": 1650.0, "note": "Annual Dental Checkup & Medicines", "days_ago": 8},
            {"kind": "expense", "category": "Shopping", "amount": 4200.0, "note": "New Running Shoes & Casual Wear", "days_ago": 6},
            {"kind": "expense", "category": "Bills", "amount": 1299.0, "note": "High-Speed Fiber Broadband & Mobile", "days_ago": 4},
            {"kind": "expense", "category": "Food", "amount": 1850.0, "note": "Team Dinner & Coffee", "days_ago": 2},
            {"kind": "expense", "category": "Entertainment", "amount": 999.0, "note": "Streaming OTT Subscriptions", "days_ago": 1},
        ]

        for tx in sample_transactions:
            tx_time = now - timedelta(days=tx["days_ago"])
            db.session.add(Transaction(
                kind=tx["kind"],
                category=tx["category"],
                amount=tx["amount"],
                note=tx["note"],
                created_at=tx_time
            ))

        # 2. Sample Budgets
        sample_budgets = [
            {"category": "Food", "limit": 9000.0},
            {"category": "Rent", "limit": 22000.0},
            {"category": "Entertainment", "limit": 4000.0},
            {"category": "Transport", "limit": 3500.0},
            {"category": "Shopping", "limit": 5000.0},
            {"category": "Utilities", "limit": 3500.0},
        ]

        for b in sample_budgets:
            db.session.add(Budget(category=b["category"], limit=b["limit"]))

        # 3. Sample Savings Goals
        sample_goals = [
            {
                "name": "Emergency Fund (6 Months)",
                "target": 150000.0,
                "saved": 95000.0,
                "deadline": (now + timedelta(days=180)).strftime("%Y-%m-%d")
            },
            {
                "name": "New Developer Laptop",
                "target": 110000.0,
                "saved": 110000.0,  # 100% complete
                "deadline": (now + timedelta(days=30)).strftime("%Y-%m-%d")
            },
            {
                "name": "Annual Vacation Trip",
                "target": 45000.0,
                "saved": 22000.0,
                "deadline": (now + timedelta(days=90)).strftime("%Y-%m-%d")
            }
        ]

        for g in sample_goals:
            db.session.add(Goal(
                name=g["name"],
                target=g["target"],
                saved=g["saved"],
                deadline=g["deadline"]
            ))

        db.session.commit()
        print("[OK] Demo data seeded successfully!")
        print(f"[OK] Transactions: {len(sample_transactions)}")
        print(f"[OK] Budgets: {len(sample_budgets)}")
        print(f"[OK] Goals: {len(sample_goals)}")

if __name__ == "__main__":
    seed_database()
