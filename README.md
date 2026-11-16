# Personal Finance Advisor Bot

An intelligent, full-featured personal finance planning web application with live tracking, budget caps, savings milestones, interactive visual analytics, and an integrated **Conversational AI Advisor Bot**.

---

## 🌟 Key Features

1. **Intelligent Dashboard**: Real-time overview of total income, expenses, net surplus, and savings rate.
2. **Transaction Tracking**: Add income and expense transactions with custom dates, categories, and notes. Filter and search transaction history.
3. **Category-wise Budgets**: Configure monthly limits per category with dynamic warning thresholds (Safe, 80%+ Warning, Exceeded Danger). Complete budget deletion and updates.
4. **Savings Goals Tracker**: Define target amounts and target deadlines. Record partial deposits, view percentage completion bars, and track milestone celebrations.
5. **Interactive AI Advisor Bot (Conversational)**:
   - Ask custom questions anytime (e.g., *"How can I save more?"*, *"Analyze my 50/30/20 rule"*, *"Can I afford a ₹15,000 expense?"*).
   - Powered by **Google Gemini 2.5 Flash** when a `GEMINI_API_KEY` is provided.
   - Seamlessly falls back to a built-in **Rule-Based Financial Expert Engine** with zero external dependencies when offline or without an API key.
6. **Visual Analytics & Reports**:
   - Expense breakdown by category (interactive Chart.js Doughnut chart).
   - Cash flow comparison (Income vs. Expense vs. Net Savings bar chart).
   - Budget vs. Actual spending comparison chart.
   - 50/30/20 guideline comparison scorecard.
7. **CSV Export**: One-click download of all transaction history in clean CSV format.
8. **Sample Data Seeder**: Standalone script (`seed_demo.py`) or one-click UI button to populate realistic demo transactions, budgets, and goals instantly.
9. **Automated Test Suite**: 12 comprehensive unit and integration tests covering all routes, CRUD operations, calculations, and AI responses.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+ (tested on Python 3.14), Flask 3.1.2, Flask-SQLAlchemy 3.1.1, python-dotenv
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, Modern CSS3 (CSS Variables, Flexbox/Grid, Responsive), Vanilla JavaScript
- **Data Visualization**: Chart.js
- **AI Intelligence**: Google Gemini API (`google-genai`), plus offline Rule-Based Expert Engine

---

## 🚀 Quick Start Guide (Windows)

### 1. Prerequisites & Installation

Open PowerShell or Command Prompt in the project directory:

```powershell
# Clone or navigate to the project directory
cd Personal_Finance_Advisor_Bot_Proper

# Install required dependencies
py -m pip install -r requirements.txt
```

*(Note: On systems where `python` is the standard alias, you can use `python` instead of `py`)*

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```

Open `.env` and add your Gemini API key if you have one:
```env
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=AIzaSy...
```
> **Note**: An API key is completely optional! The application includes an intelligent local financial advisor engine that provides customized financial analysis even without an API key.

### 3. Seed Demo Data (Optional)

To start with realistic sample transactions, budgets, and savings goals:
```powershell
py seed_demo.py
```
*(You can also click the "⚡ Seed Sample Data" button on the dashboard)*

### 4. Run the Application

```powershell
py app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🧪 Running Automated Tests

Run the full automated test suite (12 unit tests):
```powershell
py -m unittest test_app.py -v
```

---

## 📁 Project Structure

```
Personal_Finance_Advisor_Bot_Proper/
├── app.py                  # Core Flask backend, database models, AI endpoints & routes
├── seed_demo.py            # Standalone demo data seeder script
├── test_app.py             # 12-test automated unit & integration test suite
├── requirements.txt        # Python package dependencies
├── .env.example            # Sample configuration file
├── .gitignore              # Git ignore rules (.env, *.db, venv, pycache)
├── README.md               # User guide and documentation
├── PROJECT_REPORT.md       # Comprehensive academic/project report
├── static/
│   ├── app.js              # Interactive AI chatbot drawer, dynamic dropdowns, advice refresh
│   └── style.css           # Modern responsive design, progress bars, dark hero, toast notifications
└── templates/
    ├── base.html           # Master layout with header, navigation, and AI chatbot drawer
    ├── dashboard.html      # Main dashboard (transactions, budgets, goals, insights)
    └── reports.html        # Analytics page with 3 interactive Chart.js visualizations
```

---

## 💬 Suggested Questions for the AI Advisor Bot

Click the **"💬 AI Advisor Bot"** button on any page and try asking:
- *"Analyze my 50/30/20 budget breakdown"*
- *"How can I save more money this month?"*
- *"Can I afford a ₹15,000 laptop purchase?"*
- *"Check my budget status and tell me where I am overspending"*
- *"What is my savings goal progress?"*
- *"Give me an overall financial health summary"*

## Documentation Link

[https://github.com/ompatil132006-cmyk/Personal_Finance_Advisor_Bot/blob/main/Personal_Finance_Advisor_Bot_%20document_final.pdf]
