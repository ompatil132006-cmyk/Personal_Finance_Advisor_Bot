# Personal Finance Advisor Bot – Comprehensive Project Report

## 1. Executive Summary
Personal Finance Advisor Bot is a full-featured, AI-powered personal financial planning and analytics web application. Built on Python (Flask 3.1.2), SQLite, SQLAlchemy, modern CSS3, and JavaScript, the application enables users to track daily income and expenses, set category-wise monthly budget ceilings with dynamic risk thresholds, establish and monitor savings milestones, visualize cash flows through interactive Chart.js graphics, and consult a dedicated conversational AI Advisor Bot.

---

## 2. Problem Statement
Individuals frequently face difficulty maintaining disciplined financial habits due to:
1. Fragmented record-keeping across bank accounts, UPI apps, and cash transactions.
2. Inability to identify budget overruns in real-time before monthly finances are depleted.
3. Lack of actionable, personalized financial advice benchmarked to standard budgeting principles (such as the 50/30/20 rule).
4. Complex, cumbersome financial software that intimidates ordinary users.

---

## 3. Project Objectives
- **Centralized Ledger**: Record and categorize income and expenses with customizable transaction dates and notes.
- **Proactive Budgeting**: Set monthly spending caps with multi-stage indicators (Normal, 80%+ Warning, and Over-Limit alerts).
- **Milestone Planning**: Create and manage savings goals with progress tracking and celebration cues upon completion.
- **Interactive AI Assistant**: Provide an always-accessible conversational chatbot (powered by Google Gemini 2.5 Flash with an offline rule-based financial reasoning engine fallback).
- **Visual Analytics**: Render multi-dimensional financial charts (Category Doughnut, Cash Flow Bar, Budget vs. Actual comparison).
- **Data Portability**: Enable instant CSV transaction export.
- **Reliability & Testability**: Complete test automation with 100% pass rate.

---

## 4. System Architecture

The application adopts a clean Model-View-Controller (MVC) and modular layered architecture:

```
┌────────────────────────────────────────────────────────┐
│                   Presentation Layer                   │
│   HTML5 • Modern CSS3 (Variables/Flex/Grid) • JS       │
│   Interactive Chat Drawer • Chart.js Data Visuals      │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP / JSON API
┌──────────────────────────▼─────────────────────────────┐
│                   Application Layer                    │
│   Flask 3.1.2 Web Server • Jinja2 Template Engine      │
│   REST Endpoints (/api/summary, /api/ai-chat, etc.)    │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
┌──────────────▼────────────┐  ┌───────────▼─────────────┐
│       Database Layer      │  │        AI Engine        │
│  SQLite + SQLAlchemy ORM  │  │  • Google Gemini 2.5    │
│  Transactions, Budgets,   │  │  • Rule-based Financial │
│  Savings Goals            │  │    Reasoning Fallback   │
└───────────────────────────┘  └─────────────────────────┘
```

---

## 5. Functional Modules & Implementation Details

### Module 1: Transaction Ledger & Filtering
- Supported kinds: Income (Salary, Freelance, Investment, Other) and Expense (Food, Rent, Transport, Utilities, Entertainment, etc.).
- Custom date selection (defaults to current date).
- Live query filters for type (All, Income, Expense), Category, and full-text keyword search across notes.
- Secure deletion with client-side confirmation dialogs.

### Module 2: Monthly Budgets Engine
- Sets maximum spending allowances per category.
- Dynamic color-coded progress bars:
  - **Safe (Green/Blue)**: < 80% of limit consumed.
  - **Warning (Amber)**: 80% to 100% of limit consumed.
  - **Exceeded (Red)**: > 100% of limit consumed (calculates exact overage).
- Full CRUD support: Create, update limits, and delete budgets.

### Module 3: Savings Goals Management
- Goal attributes: Name, Target Amount, Saved Amount, and Target Deadline Date.
- Automatic percentage progress bar calculation and remaining fund target display.
- Incremental deposits through direct input.
- Visual milestone badge when goal reaches 100%.
- Delete goal capability.

### Module 4: Conversational AI Advisor Bot
- Accessible on all screens via a persistent floating launcher or navigation bar.
- Accepts natural-language questions regarding:
  - 50/30/20 rule customized to user's real income.
  - Actionable expense reduction strategies based on user's highest spending areas.
  - Immediate affordability evaluations (e.g., *"Can I afford a ₹15,000 phone?"*).
  - Status of budgets and savings goals.
- Dual-engine architecture:
  - Primary: Google Gemini 2.5 Flash via `google-genai` SDK when `GEMINI_API_KEY` is present.
  - Secondary: Deterministic rule-based expert engine providing intelligent answers with zero network/API dependencies.

### Module 5: Visual Reports & Analytics
- **Category Doughnut Chart**: Visualizes expenditure percentage across categories with custom tooltips.
- **Cash Flow Comparison Chart**: Contrasts Total Income, Total Expenses, and Net Savings.
- **Budget vs. Actual Chart**: Compares budgeted spending ceilings against real expenses side-by-side.
- **50/30/20 Financial Health Guide**: Benchmarks recorded earnings into theoretical Needs, Wants, and Savings buckets.

### Module 6: Data Export & Seeding
- **CSV Export**: Standardized comma-separated file download for analysis in Excel or Google Sheets.
- **Demo Data Seeder**: `seed_demo.py` and `/seed-demo` route populating 15 realistic transactions, 6 budgets, and 3 goals.

---

## 6. Verification & Quality Assurance

A dedicated automated test suite (`test_app.py`) was executed using Python's `unittest` framework:

| Test Case | Module Covered | Result |
|-----------|----------------|--------|
| `test_dashboard_empty_renders_properly` | Dashboard & Jinja2 Template Globals | Passed |
| `test_add_income_and_expense_transactions` | Transaction Creation & Date Parsing | Passed |
| `test_invalid_transaction_amount_rejected` | Server-side Input Validation | Passed |
| `test_delete_transaction` | Transaction Deletion | Passed |
| `test_budget_create_update_and_delete` | Budget Lifecycle (Create/Update/Delete) | Passed |
| `test_goals_lifecycle` | Savings Goals (Create/Deposit/Completion/Delete) | Passed |
| `test_reports_page` | Reports View & Aggregation Calculations | Passed |
| `test_api_summary` | REST JSON Summary Endpoint | Passed |
| `test_api_ai_advice` | Quick AI Advice Generator | Passed |
| `test_api_ai_chat_conversational_queries` | Interactive Chatbot (50/30/20, Affordability, Budgets) | Passed |
| `test_export_csv` | CSV Generation & Mime Header Verification | Passed |
| `test_seed_demo_route` | Database Seeder Verification | Passed |

**Test Result Summary: 12 / 12 Tests Passed (100% Pass Rate).**

---

## 7. Conclusion
The Personal Finance Advisor Bot delivers a production-grade, aesthetically pleasing, and functionally robust personal financial assistant. It bridges the gap between daily financial recording and proactive advisory through modern software engineering practices, responsive UI/UX, and hybrid AI intelligence.
