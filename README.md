# PocketTrack – Student Expense & Budget Manager
**BCA Academic Project | Full-Stack Web Application**

PocketTrack is a modern, responsive, database-driven full-stack web application developed specifically for college and university students to manage their daily expenditures, establish monthly budgets, monitor category-wise spending patterns, and prevent overspending.

Unlike static demonstrations, **PocketTrack is 100% functional**, featuring real SQLite persistence, secure Werkzeug authentication, complete CRUD operations, dynamic dashboard calculations, interactive Chart.js visualizations, and automated smart insights.

---

## Table of Contents
1. [Project Objective](#1-project-objective)
2. [Key Features](#2-key-features)
3. [Technology Stack](#3-technology-stack)
4. [MVC Architecture](#4-mvc-architecture)
5. [Database Design](#5-database-design)
6. [SDLC Documentation](#6-sdlc-documentation)
7. [Installation & Execution Guide](#7-installation--execution-guide)
8. [Automated Testing](#8-automated-testing)
9. [Security Implementation](#9-security-implementation)
10. [Future Enhancements](#10-future-enhancements)

---

## 1. Project Objective

College students frequently struggle with financial discipline due to irregular pocket money, hostel mess charges, transportation costs, and academic expenses (books, stationery, examination fees). Existing personal finance software is often overly complex, requires linking bank accounts, or is cluttered with advertisements.

**PocketTrack** bridges this gap by providing:
* A lightweight, intuitive, and student-focused financial tracking tool.
* Realistic monthly budget ceilings with proactive warning indicators.
* Comprehensive categorization tailored for college life (Food, Travel, Education, Bills, Entertainment, etc.).
* Strict user privacy and data isolation—every student manages only their private financial records.

---

## 2. Key Features

| Category | Features Included |
| :--- | :--- |
| **Authentication** | Secure student registration, email validation, Werkzeug SHA-256 password hashing, session-based login, and logout. |
| **Budgeting System** | Dynamic monthly budget setter, progress tracking, and multi-state visual alerts: **Normal** (<80%), **Warning** (80%–100%), and **Exceeded** (>100%). |
| **Expense CRUD** | Create, Read, Update, and Delete expense records with names, amounts, categories, dates, payment methods, and optional notes. |
| **Dynamic Dashboard** | Instant calculation of Monthly Budget, Total Spent, Remaining Balance, Transaction Count, and Highest Spending Category. |
| **Visual Analytics** | Interactive Doughnut Chart rendered via **Chart.js CDN** dynamically driven by SQLite database records. |
| **Smart Insights** | Rule-based financial tips generated directly from transaction data (e.g., top category, percentage used, largest expense). |
| **Search & Filtering** | Multi-criteria expense history filtering: text search, category dropdown, start/end date range, and client-side instant search. |

---

## 3. Technology Stack

* **Backend Engine:** Python 3 (Tested with Python 3.14 / 3.10+)
* **Web Framework:** Flask (Version 3.1+)
* **Database:** SQLite3
* **ORM:** SQLAlchemy / Flask-SQLAlchemy (Version 3.1+)
* **Security:** Werkzeug Security (`generate_password_hash`, `check_password_hash`)
* **Templating:** Jinja2
* **Frontend:** HTML5, CSS3 (Custom Responsive Design with Flexbox & Grid), Vanilla JavaScript
* **Data Visualization:** Chart.js (CDN)
* **Development Environment:** Visual Studio Code (VS Code) on Windows

---

## 4. MVC Architecture

PocketTrack is structured strictly adhering to the **Model-View-Controller (MVC)** architectural pattern to ensure clean separation of concerns, high maintainability, and code readability:

```
PocketTrack/
│
├── app.py                      # Flask Application Entry Point & Global Config
├── requirements.txt            # Python Dependencies
├── README.md                   # Complete Academic Project & SDLC Documentation
├── .gitignore                  # Git Ignore Configuration
├── seed_demo_data.py           # Optional Academic Evaluation Data Seeder
├── test_pockettrack.py         # Automated Test Suite (14 Unit/Integration Tests)
│
├── venv/                       # Isolated Python Virtual Environment
│
├── controllers/                # CONTROLLERS (Request Handling & Business Logic)
│   ├── __init__.py             # Blueprints export
│   ├── auth_controller.py      # Registration, Login, Logout, Session Guard
│   ├── dashboard_controller.py # Financial Aggregations, Budget Limits, Insights
│   └── expense_controller.py   # Expense CRUD, Validation, Filter Engine
│
├── models/                     # MODELS (Database Entities & Business Rules)
│   ├── __init__.py             # Model exports
│   ├── database.py             # SQLAlchemy instance initialization
│   ├── user_model.py           # User entity with password hashing methods
│   ├── budget_model.py         # Monthly Budget allocation entity
│   └── expense_model.py        # Expense transaction entity
│
├── views/                      # VIEWS (Jinja2 HTML Templates)
│   ├── base.html               # Shared Master Layout (Sidebar, Topbar, Modals)
│   ├── login.html              # Student Authentication Portal
│   ├── register.html           # New Student Onboarding
│   ├── dashboard.html          # Dynamic Analytics & Chart.js Visualizations
│   ├── add_expense.html        # Expenditure Entry Form
│   ├── edit_expense.html       # Expenditure Modification Form
│   └── expenses.html           # Filterable Transaction History Table
│
├── static/                     # STATIC ASSETS
│   ├── css/
│   │   └── style.css           # Custom Modern Styling & Responsive Layout
│   └── js/
│       └── script.js           # Chart.js handler, Modals, Real-time search
│
└── database/
    └── pockettrack.db          # Persistent SQLite Database
```

### Responsibility Breakdown:
1. **Model (`models/`):** Manages database tables, relationships, constraints, and data integrity. Models never format output for display or parse HTTP headers.
2. **View (`views/`):** Jinja2 templates render HTML dynamically based on context objects passed from controllers. Templates never perform direct database transactions.
3. **Controller (`controllers/`):** Blueprints receive incoming HTTP requests, validate input parameters, communicate with Models to retrieve or update records, and select the corresponding View to return.

---

## 5. Database Design

The relational schema is implemented in SQLite with foreign keys and cascade deletions.

```
+-----------------------------------------------------+
|                       USERS                         |
+-----------------------------------------------------+
| id            | INTEGER      | PRIMARY KEY          |
| name          | VARCHAR(100) | NOT NULL             |
| username      | VARCHAR(50)  | UNIQUE, NOT NULL     |
| email         | VARCHAR(120) | UNIQUE, NOT NULL     |
| password_hash | VARCHAR(255) | NOT NULL             |
| created_at    | DATETIME     | DEFAULT CURRENT_TIME |
+-----------------------------------------------------+
          |                               |
          | 1:N                           | 1:N
          v                               v
+-----------------------+     +-------------------------------+
|        BUDGETS        |     |           EXPENSES            |
+-----------------------+     +-------------------------------+
| id         | INTEGER  |     | id             | INTEGER      |
| user_id    | FK(users)|     | user_id        | FK(users)    |
| month      | VARCHAR  |     | expense_name   | VARCHAR(150) |
| amount     | FLOAT    |     | amount         | FLOAT        |
| created_at | DATETIME |     | category       | VARCHAR(50)  |
+-----------------------+     | expense_date   | DATE         |
                              | payment_method | VARCHAR(50)  |
                              | note           | TEXT         |
                              | created_at     | DATETIME     |
                              +-------------------------------+
```

* **Data Isolation Rule:** Every query filters strictly by `user_id = session['user_id']`. A student can never view, edit, or delete another student's budget or expenses.

---

## 6. SDLC Documentation

PocketTrack was developed following the classic **Software Development Life Cycle (SDLC)** with an iterative Waterfall approach suitable for academic assessment:

### Phase 1: Requirement Analysis
* **Problem Definition:** High failure rate among college students in tracking discretionary spending.
* **Target Audience:** BCA and university students.
* **Functional Requirements:**
  - Account creation, secure authentication, and session handling.
  - Setting and updating a target budget per calendar month.
  - Adding expenses across predefined categories (Food, Travel, Education, etc.).
  - Updating and deleting existing transactions with confirmation.
  - Real-time dashboard summaries and budget status warning alerts.
  - Search and filter by category and date range.
* **Non-Functional Requirements:**
  - Clean MVC architecture.
  - Fast response times using lightweight SQLite.
  - Responsive design functional on mobile phones and desktop browsers.

### Phase 2: System Design
* **Architectural Design:** Multi-tier MVC structure decoupling business rules from presentation.
* **Database Design:** Normalized Relational Database (3NF) preventing redundancy. Foreign key constraints ensure data integrity with cascading deletions.
* **UI/UX Design:** High-contrast dashboard cards, intuitive category badge colors, visual progress bars, and modal-based budget adjustment.

### Phase 3: Development & Implementation
* **Backend:** Flask routing organized into modular Blueprints (`auth_bp`, `dashboard_bp`, `expense_bp`).
* **Security:** Werkzeug SHA-256 password hashing; route protection using a custom `@login_required` decorator.
* **Frontend:** Semantic HTML5, CSS Grid/Flexbox layouts, and custom JavaScript for instant client-side filtering and Chart.js integration.

### Phase 4: Testing & Quality Assurance
* **Unit & Integration Testing:** Automated test suite (`test_pockettrack.py`) with 14 test cases covering:
  - Form validation (password length, password match, duplicate username/email).
  - Authentication flow (login with username vs. email, session clearance upon logout).
  - Protected route access control (redirect unauthenticated requests).
  - Expense CRUD operations.
  - Multi-user isolation (User 2 blocked from reading or altering User 1's records).
  - Budget calculations and threshold transitions (Normal, Warning at 80%, Exceeded over 100%).
* **Result:** 14/14 tests passing with zero errors.

### Phase 5: Deployment
* **Local Environment Setup:** Configured for local execution in VS Code on Windows via Python virtual environment (`venv`).
* **Production Readiness:** Configurable secret key, modular package structure, and SQLite database migration capability.

### Phase 6: Maintenance & Future Support
* **Maintainability:** Clear code comments, docstrings on all controllers/models, and centralized template layout.
* **Extensibility:** Standard SQLAlchemy models allow switching to PostgreSQL or MySQL simply by altering the database connection URI in `app.py`.

---

## 7. Installation & Execution Guide

### Prerequisites
* Windows 10/11 operating system
* Python 3.10+ installed
* Visual Studio Code (or any preferred code editor)

### Step 1: Open VS Code Terminal
Open VS Code, navigate to the `PocketTrack` directory, and open PowerShell or Command Prompt.

### Step 2: Create Python Virtual Environment
```powershell
python -m venv venv
```
*(On systems with multiple Python versions, use `py -m venv venv`)*

### Step 3: Activate the Virtual Environment
```powershell
venv\Scripts\activate
```
*(You will see `(venv)` prepended to your terminal prompt).*

### Step 4: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: (Optional) Seed Demo Student Data
If you would like to test the application immediately with realistic sample records:
```powershell
python seed_demo_data.py
```
**Demo Account Credentials:**
* **Username:** `rahul` (or email: `rahul@college.edu`)
* **Password:** `student123`

*(Alternatively, you can skip seeding and create your own fresh account from the registration page).*

### Step 6: Start the Application Server
```powershell
python app.py
```

### Step 7: Access PocketTrack
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 8. Automated Testing

PocketTrack includes a built-in automated test suite covering all critical workflows.

To run all 14 tests:
```powershell
python test_pockettrack.py
```

Expected Output:
```text
..............
----------------------------------------------------------------------
Ran 14 tests in 4.215s

OK
```

---

## 9. Security Implementation

1. **Password Hashing:** Passwords are never stored in plain text. PocketTrack uses Werkzeug's `generate_password_hash` using salted hashes.
2. **Session Hijacking Mitigation:** Flask sessions are cryptographically signed with a secure server-side `SECRET_KEY`.
3. **Route Protection:** All financial routes are guarded with `@login_required`. Attempting to access `/dashboard` or `/expenses` without an active session redirects to `/login`.
4. **Tenant Isolation:** All expense and budget queries explicitly constrain `user_id = session['user_id']`. Directly guessing IDs in URLs (`/edit-expense/99`) aborts with an authorization error.
5. **SQL Injection Prevention:** Parameterized queries and SQLAlchemy ORM completely prevent SQL injection attacks.
6. **Cross-Site Scripting (XSS) Prevention:** Jinja2 auto-escapes all dynamic content by default.

---

## 10. Future Enhancements

* **Export Reports:** Export expense statements to PDF and CSV/Excel formats for submission to parents or guardians.
* **Split Bills:** Classmate group expense splitting with automatic per-person balance calculation.
* **Receipt Image Uploads:** Attach photos of store receipts to individual expense records.
* **Email Overspend Alerts:** Automated notification when budget reaches 90%.
