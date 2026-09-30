import csv
import io
import os
import re
from datetime import datetime, timezone, date
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash
from flask_sqlalchemy import SQLAlchemy

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "finance-advisor-demo-key-123")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance_advisor.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Expose helper functions to Jinja2 templates
app.jinja_env.globals.update(min=min, max=max)

CATEGORIES = [
    "Food", "Rent", "Transport", "Education", "Entertainment",
    "Healthcare", "Shopping", "Utilities", "Bills", "Salary", "Freelance", "Investment", "Other"
]

EXPENSE_CATEGORIES = [
    "Food", "Rent", "Transport", "Education", "Entertainment",
    "Healthcare", "Shopping", "Utilities", "Bills", "Other"
]

INCOME_CATEGORIES = [
    "Salary", "Freelance", "Investment", "Other"
]

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(20), nullable=False)  # "income" or "expense"
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200), default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @property
    def formatted_date(self):
        return self.created_at.strftime("%d %b %Y")

    @property
    def input_date(self):
        return self.created_at.strftime("%Y-%m-%d")

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), unique=True, nullable=False)
    limit = db.Column(db.Float, nullable=False)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target = db.Column(db.Float, nullable=False)
    saved = db.Column(db.Float, default=0, nullable=False)
    deadline = db.Column(db.String(20), default="")

    @property
    def pct(self):
        if self.target <= 0:
            return 0
        return min(100.0, round((self.saved / self.target) * 100, 1))

    @property
    def remaining(self):
        return max(0.0, self.target - self.saved)

    @property
    def is_completed(self):
        return self.saved >= self.target


def totals():
    income = sum(t.amount for t in Transaction.query.filter_by(kind="income").all())
    expense = sum(t.amount for t in Transaction.query.filter_by(kind="expense").all())
    return income, expense, income - expense


def category_spending():
    data = {c: 0.0 for c in EXPENSE_CATEGORIES}
    for t in Transaction.query.filter_by(kind="expense").all():
        data[t.category] = data.get(t.category, 0.0) + t.amount
    return data


def insights():
    income, expense, balance = totals()
    spending = category_spending()
    tips = []

    if income == 0 and expense == 0:
        return [
            "Start by adding your income and expenses. Your dashboard will generate insights automatically.",
            "Try adding a budget for common expenses like Food or Transport to stay on track."
        ]

    if income > 0:
        ratio = (expense / income) * 100
        savings_rate = ((income - expense) / income) * 100
        if ratio > 85:
            tips.append(f"Expenses are {ratio:.0f}% of income (high). Review non-essential spending to build a buffer.")
        elif ratio > 65:
            tips.append(f"Expenses are {ratio:.0f}% of income. Aim to increase your savings rate towards 20% or more.")
        else:
            tips.append(f"Healthy financial balance! You are saving {savings_rate:.0f}% of your recorded income.")
    elif expense > 0:
        tips.append("No income recorded yet. Please add your monthly income to get accurate savings calculations.")

    if balance > 0:
        tips.append(f"You have a surplus of ₹{balance:,.0f}. Consider allocating part of it to an active savings goal.")
    elif balance < 0:
        tips.append(f"Expenses exceed income by ₹{abs(balance):,.0f}. Prioritize needs and cut discretionary categories.")

    # Top spending category
    active_expenses = {k: v for k, v in spending.items() if v > 0}
    if active_expenses:
        top_cat = max(active_expenses, key=active_expenses.get)
        tips.append(f"Top expense category: {top_cat} (₹{active_expenses[top_cat]:,.0f}).")

    # Budget warnings and alerts
    for b in Budget.query.all():
        spent = spending.get(b.category, 0.0)
        if spent > b.limit:
            over = spent - b.limit
            tips.append(f"Budget Alert: {b.category} is ₹{over:,.0f} over its ₹{b.limit:,.0f} limit!")
        elif spent >= 0.8 * b.limit and b.limit > 0:
            tips.append(f"Budget Warning: {b.category} is at {(spent/b.limit)*100:.0f}% of its ₹{b.limit:,.0f} limit.")

    # Goals updates
    goals = Goal.query.all()
    completed_goals = [g for g in goals if g.is_completed]
    if completed_goals:
        tips.append(f"Goal Achieved: '{completed_goals[0].name}' has reached 100% of its target!")
    elif goals:
        closest = max(goals, key=lambda g: g.pct)
        if closest.pct > 0:
            tips.append(f"Savings Goal '{closest.name}' is {closest.pct:.0f}% funded (₹{closest.remaining:,.0f} remaining).")

    return tips[:7]


def get_local_ai_response(user_message, financial_summary):
    """
    Intelligent rule-based personal finance advisor that responds conversationally
    when Gemini API is not configured or offline.
    """
    msg = user_message.lower().strip()
    income = financial_summary.get("income", 0)
    expense = financial_summary.get("expense", 0)
    balance = financial_summary.get("balance", 0)
    spending = financial_summary.get("spending", {})
    budgets = financial_summary.get("budgets", [])
    goals = financial_summary.get("goals", [])

    savings_rate = ((income - expense) / income * 100) if income > 0 else 0

    # 1. 50/30/20 Rule Analysis
    if any(k in msg for k in ["50/30/20", "50 30 20", "rule", "split", "ratio", "budget rule"]):
        if income > 0:
            needs = income * 0.50
            wants = income * 0.30
            savings = income * 0.20
            return (
                f"📊 **50/30/20 Budget Breakdown for your income (₹{income:,.0f}):**\n\n"
                f"• **50% Needs (Essential):** ₹{needs:,.0f} (Rent, Utilities, Food, Healthcare)\n"
                f"• **30% Wants (Discretionary):** ₹{wants:,.0f} (Entertainment, Shopping, Dining)\n"
                f"• **20% Savings & Debt:** ₹{savings:,.0f} (Emergency Fund, Investments, Goals)\n\n"
                f"Currently, your total spending is ₹{expense:,.0f} ({expense/income*100:.1f}% of income), "
                f"leaving ₹{balance:,.0f} as net balance. Try categorizing your expenses to see if your 'Needs' stay under 50%!"
            )
        else:
            return (
                "The **50/30/20 rule** recommends dividing your after-tax income into:\n"
                "• **50% Needs:** Essential bills, groceries, housing, utilities.\n"
                "• **30% Wants:** Dining out, hobbies, subscriptions, entertainment.\n"
                "• **20% Savings:** Emergency fund, retirement, investments, debt prepayment.\n\n"
                "💡 Record your monthly income in the dashboard to see your custom rupee targets!"
            )

    # 2. Saving money / Cut spending
    if any(k in msg for k in ["save", "saving", "cut", "reduce", "spend less", "how can i save"]):
        top_cats = sorted(spending.items(), key=lambda x: x[1], reverse=True)
        top_active = [c for c in top_cats if c[1] > 0][:3]
        advice = "💡 **Actionable Ways to Save More:**\n\n"
        if top_active:
            advice += f"Your top spending areas right now are:\n"
            for cat, amt in top_active:
                advice += f"• **{cat}**: ₹{amt:,.0f} ({(amt/expense*100):.0f}% of spending)\n"
            advice += "\n**Recommendations:**\n"
            advice += "1. **Cut 10-15% from Discretionary**: Dining out and Shopping are easiest to trim.\n"
            advice += "2. **Audit Subscriptions**: Cancel recurring services you haven't used this month.\n"
            advice += "3. **Set Category Budgets**: Set spending caps right here in the 'Monthly Budgets' section!\n"
            advice += f"4. **Automate Savings**: Allocate your current ₹{max(0, balance):,.0f} surplus directly into your active goals."
        else:
            advice += (
                "1. **Track Every Rupee**: Keep recording daily transactions to reveal hidden leaks.\n"
                "2. **The 24-Hour Rule**: Wait 24 hours before making any impulse purchase over ₹1,000.\n"
                "3. **Zero-Sum Budgeting**: Assign every rupee a job before the month starts.\n"
                "4. **Emergency Fund First**: Build 3 to 6 months of living expenses."
            )
        return advice

    # 3. Budget Status
    if any(k in msg for k in ["budget", "over budget", "limit", "budgets"]):
        if not budgets:
            return (
                "You haven't set any monthly budgets yet! 🎯\n\n"
                "Setting limits helps prevent overspending before month-end. "
                "You can add a budget for categories like Food, Entertainment, or Shopping on your dashboard."
            )
        exceeded = [b for b in budgets if b["spent"] > b["limit"]]
        warning = [b for b in budgets if 0.8 * b["limit"] <= b["spent"] <= b["limit"]]
        safe = [b for b in budgets if b["spent"] < 0.8 * b["limit"]]

        res = "📋 **Your Budget Health Check:**\n\n"
        if exceeded:
            res += "⚠️ **Over Budget:**\n"
            for b in exceeded:
                res += f"• **{b['category']}**: Spent ₹{b['spent']:,.0f} / Limit ₹{b['limit']:,.0f} (Exceeded by ₹{b['spent']-b['limit']:,.0f}!)\n"
        if warning:
            res += "\n⚡ **Close to Limit (80%+):**\n"
            for b in warning:
                res += f"• **{b['category']}**: Spent ₹{b['spent']:,.0f} / Limit ₹{b['limit']:,.0f} ({(b['spent']/b['limit'])*100:.0f}%)\n"
        if safe:
            res += "\n✅ **Within Safe Limits:**\n"
            for b in safe:
                res += f"• **{b['category']}**: Spent ₹{b['spent']:,.0f} / Limit ₹{b['limit']:,.0f}\n"
        return res

    # 4. Goals Status
    if any(k in msg for k in ["goal", "goals", "target", "vacation", "emergency fund", "laptop"]):
        if not goals:
            return (
                "You don't have any active savings goals yet. 🎯\n\n"
                "Creating goals (like an Emergency Fund, Vacation, or New Gadget) gives your money purpose! "
                "Use the 'Savings Goals' card on the dashboard to create one."
            )
        res = "🎯 **Your Savings Goals Progress:**\n\n"
        for g in goals:
            pct = min(100.0, (g.saved / g.target * 100)) if g.target else 0
            status_icon = "🎉 Completed!" if g.saved >= g.target else f"{pct:.0f}% complete"
            res += f"• **{g.name}**: Saved ₹{g.saved:,.0f} of ₹{g.target:,.0f} ({status_icon})"
            if g.deadline:
                res += f" — Deadline: {g.deadline}"
            res += "\n"
        if balance > 0:
            res += f"\n💡 Tip: You currently have ₹{balance:,.0f} in surplus balance that you can deposit into a goal!"
        return res

    # 5. Can I afford X?
    afford_match = re.search(r"afford\s*(?:a|an)?\s*([a-zA-Z0-9\s]+)?", msg)
    if "afford" in msg:
        # Check if an amount is mentioned
        amounts = re.findall(r"(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*(?:\.\d+)?)", msg)
        query_amt = None
        for a in amounts:
            try:
                val = float(a.replace(",", ""))
                if val > 50:
                    query_amt = val
                    break
            except ValueError:
                pass

        if query_amt:
            if balance >= query_amt:
                rem = balance - query_amt
                return (
                    f"✅ **Yes, based on current figures you can afford it!**\n\n"
                    f"• Purchase amount: ₹{query_amt:,.0f}\n"
                    f"• Current available surplus: ₹{balance:,.0f}\n"
                    f"• Remaining surplus after purchase: ₹{rem:,.0f}\n\n"
                    f"💡 Make sure this purchase doesn't take away from any critical upcoming bills or emergency savings!"
                )
            else:
                deficit = query_amt - balance
                return (
                    f"⚠️ **Caution: This would exceed your current net balance.**\n\n"
                    f"• Purchase amount: ₹{query_amt:,.0f}\n"
                    f"• Current recorded surplus: ₹{balance:,.0f}\n"
                    f"• Shortfall: ₹{deficit:,.0f}\n\n"
                    f"💡 Consider creating a dedicated **Savings Goal** for this item and saving towards it gradually!"
                )
        else:
            return (
                f"You currently have a recorded balance surplus of ₹{balance:,.0f} (Income ₹{income:,.0f} − Expenses ₹{expense:,.0f}).\n"
                f"Mention the price (e.g. 'Can I afford a 15000 phone?') and I'll analyze it against your available surplus!"
            )

    # 6. Overall Financial Health / Summary
    if any(k in msg for k in ["summary", "health", "how am i doing", "status", "overview", "hello", "hi", "hey"]):
        greeting = "Hello! " if any(k in msg for k in ["hello", "hi", "hey"]) else ""
        return (
            f"{greeting}Here is your **Personal Financial Health Summary**:\n\n"
            f"• **Total Income:** ₹{income:,.0f}\n"
            f"• **Total Expenses:** ₹{expense:,.0f}\n"
            f"• **Net Balance:** ₹{balance:,.0f}\n"
            f"• **Savings Rate:** {savings_rate:.1f}%\n"
            f"• **Active Budgets:** {len(budgets)}\n"
            f"• **Active Goals:** {len(goals)}\n\n"
            f"💡 **Advisor Note:** " + (
                "You have a solid positive cash flow. Keep funding your goals!" if balance > 0
                else "Watch out for higher spending than income this period."
            ) + "\n\nAsk me anything! For example: *'How can I save more?'*, *'Analyze my 50/30/20 rule'*, or *'Check my budgets'*."
        )

    # General default response
    return (
        "I am your Personal Finance Advisor Bot! 🤖 Here are things you can ask me:\n\n"
        "• *'Analyze my 50/30/20 budget'* — see your ideal breakdown.\n"
        "• *'How can I save more money?'* — get personalized tips on your highest spending.\n"
        "• *'Can I afford a ₹10,000 expense?'* — check against current cashflow.\n"
        "• *'Check my budget status'* — see which categories are near or over limit.\n"
        "• *'What is my savings goal progress?'* — track your targets.\n"
        "• *'Give me an overall financial summary'* — instant health check."
    )


# ----------------- ROUTES ----------------- #

@app.route("/")
def dashboard():
    income, expense, balance = totals()
    spending = category_spending()

    # Query params for filtering transactions
    kind_filter = request.args.get("kind", "").strip().lower()
    category_filter = request.args.get("category", "").strip()
    search_query = request.args.get("search", "").strip()

    t_query = Transaction.query
    if kind_filter in ["income", "expense"]:
        t_query = t_query.filter(Transaction.kind == kind_filter)
    if category_filter and category_filter in CATEGORIES:
        t_query = t_query.filter(Transaction.category == category_filter)
    if search_query:
        t_query = t_query.filter(Transaction.note.ilike(f"%{search_query}%"))

    transactions = t_query.order_by(Transaction.created_at.desc()).limit(30).all()
    total_tx_count = Transaction.query.count()

    budgets = Budget.query.order_by(Budget.category).all()
    goals = Goal.query.order_by(Goal.id.desc()).all()

    budget_rows = []
    for b in budgets:
        spent = spending.get(b.category, 0.0)
        pct = min((spent / b.limit * 100) if b.limit > 0 else 0, 100.0)
        status = "danger" if spent > b.limit else ("warning" if spent >= 0.8 * b.limit else "safe")
        budget_rows.append({
            "id": b.id,
            "category": b.category,
            "limit": b.limit,
            "spent": spent,
            "pct": round(pct, 1),
            "status": status,
            "remaining": max(0.0, b.limit - spent)
        })

    # Today's date string for transaction default
    today_str = date.today().strftime("%Y-%m-%d")

    return render_template(
        "dashboard.html",
        income=income,
        expense=expense,
        balance=balance,
        transactions=transactions,
        total_tx_count=total_tx_count,
        budgets=budget_rows,
        goals=goals,
        spending=spending,
        categories=CATEGORIES,
        expense_categories=EXPENSE_CATEGORIES,
        income_categories=INCOME_CATEGORIES,
        insights=insights(),
        today_str=today_str,
        kind_filter=kind_filter,
        category_filter=category_filter,
        search_query=search_query
    )


@app.post("/transactions/add")
def add_transaction():
    try:
        amount = float(request.form["amount"])
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        kind = request.form["kind"].strip().lower()
        if kind not in ["income", "expense"]:
            raise ValueError("Invalid transaction kind.")

        category = request.form["category"].strip()
        note = request.form.get("note", "").strip()

        # Handle custom date if provided
        tx_date_str = request.form.get("date", "").strip()
        if tx_date_str:
            try:
                # Combine custom date with current time
                parsed_date = datetime.strptime(tx_date_str, "%Y-%m-%d")
                now = datetime.now()
                tx_datetime = parsed_date.replace(hour=now.hour, minute=now.minute, second=now.second)
            except ValueError:
                tx_datetime = datetime.now(timezone.utc)
        else:
            tx_datetime = datetime.now(timezone.utc)

        db.session.add(Transaction(
            kind=kind,
            category=category,
            amount=amount,
            note=note,
            created_at=tx_datetime
        ))
        db.session.commit()
        flash("Transaction recorded successfully!", "success")
    except Exception as e:
        flash(f"Error adding transaction: {str(e) if str(e) else 'Invalid details'}", "error")

    return redirect(url_for("dashboard"))


@app.post("/transactions/<int:tid>/delete")
def delete_transaction(tid):
    t = db.session.get(Transaction, tid)
    if t:
        db.session.delete(t)
        db.session.commit()
        flash("Transaction deleted.", "success")
    else:
        flash("Transaction not found.", "error")
    return redirect(url_for("dashboard"))


@app.post("/budgets/save")
def save_budget():
    try:
        category = request.form["category"].strip()
        limit = float(request.form["limit"])
        if limit <= 0:
            raise ValueError("Budget limit must be positive.")

        b = Budget.query.filter_by(category=category).first()
        if b:
            b.limit = limit
            flash(f"Updated budget for {category} to ₹{limit:,.0f}.", "success")
        else:
            db.session.add(Budget(category=category, limit=limit))
            flash(f"Created budget for {category} at ₹{limit:,.0f}.", "success")
        db.session.commit()
    except Exception as e:
        flash(f"Could not save budget: {str(e) if str(e) else 'Invalid limit'}", "error")

    return redirect(url_for("dashboard"))


@app.post("/budgets/<int:bid>/delete")
def delete_budget(bid):
    b = db.session.get(Budget, bid)
    if b:
        cat = b.category
        db.session.delete(b)
        db.session.commit()
        flash(f"Deleted budget for {cat}.", "success")
    else:
        flash("Budget not found.", "error")
    return redirect(url_for("dashboard"))


@app.post("/goals/add")
def add_goal():
    try:
        name = request.form["name"].strip()
        if not name:
            raise ValueError("Goal name is required.")
        target = float(request.form["target"])
        saved = float(request.form.get("saved", 0) or 0)
        if target <= 0 or saved < 0:
            raise ValueError("Target must be positive, saved cannot be negative.")

        deadline = request.form.get("deadline", "").strip()

        db.session.add(Goal(
            name=name,
            target=target,
            saved=saved,
            deadline=deadline
        ))
        db.session.commit()
        flash(f"Savings goal '{name}' created!", "success")
    except Exception as e:
        flash(f"Invalid goal details: {str(e) if str(e) else 'Please check your inputs'}", "error")

    return redirect(url_for("dashboard"))


@app.post("/goals/<int:gid>/add")
def add_goal_saving(gid):
    goal = db.session.get(Goal, gid)
    if goal:
        try:
            amount = float(request.form["amount"])
            if amount <= 0:
                raise ValueError("Deposit amount must be positive.")
            goal.saved = min(goal.saved + amount, goal.target)
            db.session.commit()
            if goal.is_completed:
                flash(f"🎉 Congratulations! You reached your goal for '{goal.name}'!", "success")
            else:
                flash(f"Added ₹{amount:,.0f} towards '{goal.name}'.", "success")
        except Exception as e:
            flash(f"Could not update goal: {str(e) if str(e) else 'Invalid amount'}", "error")
    return redirect(url_for("dashboard"))


@app.post("/goals/<int:gid>/delete")
def delete_goal(gid):
    goal = db.session.get(Goal, gid)
    if goal:
        name = goal.name
        db.session.delete(goal)
        db.session.commit()
        flash(f"Goal '{name}' removed.", "success")
    else:
        flash("Goal not found.", "error")
    return redirect(url_for("dashboard"))


@app.get("/reports")
def reports():
    income, expense, balance = totals()
    spending = category_spending()

    # Active expense categories
    expense_labels = [k for k, v in spending.items() if v > 0]
    expense_values = [spending[k] for k in expense_labels]

    # If no expenses, fallback to all categories with 0
    if not expense_labels:
        expense_labels = EXPENSE_CATEGORIES
        expense_values = [0 for _ in expense_labels]

    # Budget vs Actual comparison
    budgets = Budget.query.order_by(Budget.category).all()
    budget_labels = [b.category for b in budgets]
    budget_limits = [b.limit for b in budgets]
    budget_actuals = [spending.get(b.category, 0.0) for b in budgets]

    savings_rate = round(((balance / income) * 100), 1) if income > 0 else 0
    expense_ratio = round(((expense / income) * 100), 1) if income > 0 else 0

    return render_template(
        "reports.html",
        income=income,
        expense=expense,
        balance=balance,
        savings_rate=savings_rate,
        expense_ratio=expense_ratio,
        labels=expense_labels,
        values=expense_values,
        budget_labels=budget_labels,
        budget_limits=budget_limits,
        budget_actuals=budget_actuals,
        insights=insights()
    )


@app.get("/api/summary")
def api_summary():
    income, expense, balance = totals()
    budgets = [{"category": b.category, "limit": b.limit} for b in Budget.query.all()]
    goals = [{"name": g.name, "target": g.target, "saved": g.saved, "deadline": g.deadline} for g in Goal.query.all()]
    return jsonify({
        "income": income,
        "expense": expense,
        "balance": balance,
        "savings_rate": round(((balance / income) * 100), 1) if income > 0 else 0,
        "category_spending": category_spending(),
        "budgets": budgets,
        "goals": goals,
        "insights": insights()
    })


@app.get("/api/ai-advice")
def ai_advice():
    key = os.getenv("GEMINI_API_KEY")
    local = insights()

    if not key:
        return jsonify({"provider": "Local Expert", "advice": local})

    try:
        from google import genai
        client = genai.Client(api_key=key)
        income, expense, balance = totals()
        prompt = f"""
You are a friendly personal finance educator.
Analyze this user's current finances and provide 4 concise, practical bullet points.
Currency: INR (₹).
Income: ₹{income:,.2f}
Expenses: ₹{expense:,.2f}
Net Balance: ₹{balance:,.2f}
Category Spending: {category_spending()}
Budgets: {[{b.category: b.limit} for b in Budget.query.all()]}
Goals: {[{g.name: f"{g.saved}/{g.target}"} for g in Goal.query.all()]}

Guidelines:
1. Be encouraging, realistic, and actionable.
2. Focus on budgeting, emergency fund buffer, and achieving goals.
3. Keep each bullet point to 1-2 clear sentences.
4. Do not offer regulated stock or cryptocurrency investment guarantees.
"""
        result = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        # Parse bullet points into clean list
        lines = [line.strip().lstrip("•*- ").strip() for line in result.text.split("\n") if line.strip()]
        advice_list = [l for l in lines if len(l) > 10][:5]
        return jsonify({"provider": "Gemini 2.5 Flash", "advice": advice_list or [result.text]})
    except Exception as e:
        return jsonify({"provider": "Local Expert", "advice": local, "error_fallback": str(e)})


@app.post("/api/ai-chat")
def ai_chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a question so I can help you with your finances!"})

    income, expense, balance = totals()
    spending = category_spending()
    budgets = [{"category": b.category, "limit": b.limit, "spent": spending.get(b.category, 0)} for b in Budget.query.all()]
    goals = Goal.query.all()

    financial_summary = {
        "income": income,
        "expense": expense,
        "balance": balance,
        "spending": spending,
        "budgets": budgets,
        "goals": goals
    }

    key = os.getenv("GEMINI_API_KEY")

    if key:
        try:
            from google import genai
            client = genai.Client(api_key=key)
            system_prompt = f"""
You are "FinanceAdvisor Bot", an intelligent, empathetic, and knowledgeable AI personal finance assistant.
You help users budget effectively, optimize expenses, build emergency savings, and reach financial goals.
Respond directly in well-formatted markdown with emojis and bullet points where helpful. Keep responses concise and practical.

Live Financial Snapshot for this user:
- Total Income: ₹{income:,.2f}
- Total Expenses: ₹{expense:,.2f}
- Net Balance: ₹{balance:,.2f}
- Category Spending: {spending}
- Budgets: {budgets}
- Goals: {[{'name': g.name, 'target': g.target, 'saved': g.saved, 'deadline': g.deadline} for g in goals]}

User question: {user_message}
"""
            result = client.models.generate_content(model="gemini-2.5-flash", contents=system_prompt)
            return jsonify({
                "provider": "Gemini 2.5 Flash",
                "reply": result.text
            })
        except Exception:
            # Fallback smoothly to local expert
            local_reply = get_local_ai_response(user_message, financial_summary)
            return jsonify({
                "provider": "Local Expert",
                "reply": local_reply
            })
    else:
        # Smart local finance logic
        local_reply = get_local_ai_response(user_message, financial_summary)
        return jsonify({
            "provider": "Local Expert",
            "reply": local_reply
        })


@app.get("/export/csv")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Type", "Category", "Amount", "Note", "Date"])
    for t in Transaction.query.order_by(Transaction.created_at.desc()).all():
        writer.writerow([
            t.id,
            t.kind.capitalize(),
            t.category,
            f"{t.amount:.2f}",
            t.note,
            t.created_at.strftime("%Y-%m-%d %H:%M")
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=finance_transactions.csv"}
    )


@app.route("/seed-demo", methods=["GET", "POST"])
def seed_demo_route():
    """Populates realistic demo financial data for demonstration."""
    from seed_demo import seed_database
    seed_database()
    flash("Demo data loaded successfully! You can explore all features.", "success")
    return redirect(url_for("dashboard"))


# Create tables on startup
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
