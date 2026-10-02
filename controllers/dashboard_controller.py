"""
Dashboard controller for PocketTrack.
Calculates dynamic student financial statistics, budget status, category analysis,
smart insights, and handles monthly budget settings.
"""
from datetime import datetime, date
from calendar import monthrange
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import func
from models import db, User, Budget, Expense
from controllers.auth_controller import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def home():
    """Redirect home route to dashboard if logged in, otherwise to login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Main student dashboard displaying dynamic analytics, budget status,
    category breakdown for Chart.js, smart insights, and recent transactions.
    """
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    # Determine current month and date range
    today = date.today()
    current_month_str = today.strftime('%Y-%m')  # e.g., '2026-10'
    month_name = today.strftime('%B %Y')         # e.g., 'October 2026'

    start_date = date(today.year, today.month, 1)
    _, last_day = monthrange(today.year, today.month)
    end_date = date(today.year, today.month, last_day)

    # 1. Fetch current monthly budget
    budget_record = Budget.query.filter_by(user_id=user_id, month=current_month_str).first()
    monthly_budget = float(budget_record.amount) if budget_record else 0.0

    # 2. Query monthly expenses for the logged-in student
    monthly_expenses_query = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    )

    monthly_expenses = monthly_expenses_query.all()
    expense_count = len(monthly_expenses)
    total_spent = sum(e.amount for e in monthly_expenses)

    # 3. Calculate remaining budget and budget health state
    remaining_budget = monthly_budget - total_spent
    budget_percentage = (total_spent / monthly_budget * 100) if monthly_budget > 0 else 0.0

    # Determine visual state: 'normal', 'warning', 'exceeded', or 'not_set'
    if monthly_budget == 0:
        budget_status = 'not_set'
        budget_message = "No monthly budget set yet. Set a budget to track your spending!"
    elif total_spent > monthly_budget:
        budget_status = 'exceeded'
        over_by = total_spent - monthly_budget
        budget_message = f"Budget exceeded by ₹{over_by:,.2f}."
    elif budget_percentage >= 80.0:
        budget_status = 'warning'
        budget_message = f"Warning: You have used {budget_percentage:.1f}% of your monthly budget."
    else:
        budget_status = 'normal'
        budget_message = f"₹{remaining_budget:,.2f} remaining within your budget."

    # 4. Category-wise spending calculation for database-driven Chart.js
    category_totals = (
        db.session.query(Expense.category, func.sum(Expense.amount).label('total'))
        .filter(
            Expense.user_id == user_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    category_labels = [row.category for row in category_totals]
    category_values = [round(float(row.total), 2) for row in category_totals]

    # 5. Highest spending category
    if category_totals:
        highest_category = category_totals[0].category
        highest_category_amount = float(category_totals[0].total)
    else:
        highest_category = "None"
        highest_category_amount = 0.0

    # 6. Recent expenses (last 5 records)
    recent_expenses = (
        Expense.query.filter_by(user_id=user_id)
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .limit(5)
        .all()
    )

    # 7. Generate Smart Insights based purely on database data
    insights = []
    if highest_category != "None":
        insights.append(f"Your highest spending category is {highest_category} with ₹{highest_category_amount:,.2f}.")

    if monthly_budget > 0:
        insights.append(f"You have used {budget_percentage:.1f}% of your monthly budget.")
        if remaining_budget >= 0:
            insights.append(f"Your remaining budget for {month_name} is ₹{remaining_budget:,.2f}.")
        else:
            insights.append(f"You are currently ₹{abs(remaining_budget):,.2f} over your planned budget.")
    else:
        insights.append("Tip: Setting a monthly budget helps PocketTrack alert you before you overspend.")

    if expense_count > 0:
        insights.append(f"You have recorded {expense_count} expense{'s' if expense_count != 1 else ''} this month.")
        # Find largest single transaction
        max_expense = max(monthly_expenses, key=lambda x: x.amount)
        insights.append(f"Single largest expense: '{max_expense.expense_name}' of ₹{max_expense.amount:,.2f} ({max_expense.category}).")
    else:
        insights.append(f"No expenses logged yet for {month_name}. Start tracking by adding your daily spends!")

    return render_template(
        'dashboard.html',
        user=user,
        month_name=month_name,
        current_month_str=current_month_str,
        monthly_budget=monthly_budget,
        total_spent=total_spent,
        remaining_budget=remaining_budget,
        expense_count=expense_count,
        highest_category=highest_category,
        highest_category_amount=highest_category_amount,
        budget_status=budget_status,
        budget_message=budget_message,
        budget_percentage=round(budget_percentage, 1),
        category_labels=category_labels,
        category_values=category_values,
        recent_expenses=recent_expenses,
        insights=insights
    )


@dashboard_bp.route('/set-budget', methods=['POST'])
@login_required
def set_budget():
    """Allow students to create or update their monthly budget limit."""
    user_id = session['user_id']
    amount_str = request.form.get('amount', '').strip()
    month = request.form.get('month', '').strip()

    if not month:
        month = date.today().strftime('%Y-%m')

    try:
        amount = float(amount_str)
        if amount < 0:
            flash('Budget amount cannot be negative.', 'danger')
            return redirect(url_for('dashboard.index'))
    except ValueError:
        flash('Please enter a valid numeric budget amount.', 'danger')
        return redirect(url_for('dashboard.index'))

    # Check if budget for this month exists
    budget_record = Budget.query.filter_by(user_id=user_id, month=month).first()
    if budget_record:
        budget_record.amount = amount
        flash(f'Monthly budget updated to ₹{amount:,.2f} successfully!', 'success')
    else:
        budget_record = Budget(user_id=user_id, month=month, amount=amount)
        db.session.add(budget_record)
        flash(f'Monthly budget of ₹{amount:,.2f} set successfully!', 'success')

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Failed to save budget. Please try again.', 'danger')

    return redirect(url_for('dashboard.index'))
