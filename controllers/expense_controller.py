"""
Expense controller for PocketTrack.
Handles expense creation, listing, searching, filtering, editing, and deletion.
Enforces strict user isolation so students can only manage their own data.
"""
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Expense
from controllers.auth_controller import login_required

expense_bp = Blueprint('expense', __name__)

# Standard categories and payment methods
CATEGORIES = [
    'Food',
    'Travel',
    'Education',
    'Shopping',
    'Entertainment',
    'Health',
    'Bills',
    'Other'
]

PAYMENT_METHODS = [
    'Cash',
    'UPI',
    'Debit Card',
    'Credit Card',
    'Other'
]


@expense_bp.route('/expenses', methods=['GET'])
@login_required
def list_expenses():
    """
    Display expense history for the logged-in student with dynamic filtering:
    search query, category filter, and start/end date range.
    """
    user_id = session['user_id']

    # Filter parameters from query string
    search_query = request.args.get('search', '').strip()
    selected_category = request.args.get('category', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()

    # Base query restricted strictly to current student
    query = Expense.query.filter_by(user_id=user_id)

    # Apply search filter
    if search_query:
        query = query.filter(
            (Expense.expense_name.ilike(f"%{search_query}%")) |
            (Expense.note.ilike(f"%{search_query}%"))
        )

    # Apply category filter
    if selected_category and selected_category in CATEGORIES:
        query = query.filter(Expense.category == selected_category)

    # Apply date filters
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Expense.expense_date >= start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Expense.expense_date <= end_date)
        except ValueError:
            pass

    # Order by date descending, then id descending
    expenses = query.order_by(Expense.expense_date.desc(), Expense.id.desc()).all()

    # Calculate summary metrics for current filtered view
    total_amount = sum(e.amount for e in expenses)
    expense_count = len(expenses)

    return render_template(
        'expenses.html',
        expenses=expenses,
        categories=CATEGORIES,
        total_amount=total_amount,
        expense_count=expense_count,
        search_query=search_query,
        selected_category=selected_category,
        start_date_str=start_date_str,
        end_date_str=end_date_str
    )


@expense_bp.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    """Add a new student expense record."""
    user_id = session['user_id']

    if request.method == 'POST':
        expense_name = request.form.get('expense_name', '').strip()
        amount_str = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        date_str = request.form.get('expense_date', '').strip()
        payment_method = request.form.get('payment_method', '').strip()
        note = request.form.get('note', '').strip()

        # Validation
        if not expense_name:
            flash('Expense Name is required.', 'danger')
            return render_template('add_expense.html', categories=CATEGORIES, payment_methods=PAYMENT_METHODS, form_data=request.form)

        try:
            amount = float(amount_str)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('add_expense.html', categories=CATEGORIES, payment_methods=PAYMENT_METHODS, form_data=request.form)
        except ValueError:
            flash('Please enter a valid numeric amount.', 'danger')
            return render_template('add_expense.html', categories=CATEGORIES, payment_methods=PAYMENT_METHODS, form_data=request.form)

        if not category or category not in CATEGORIES:
            flash('Please select a valid expense category.', 'danger')
            return render_template('add_expense.html', categories=CATEGORIES, payment_methods=PAYMENT_METHODS, form_data=request.form)

        try:
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Please provide a valid date (YYYY-MM-DD).', 'danger')
            return render_template('add_expense.html', categories=CATEGORIES, payment_methods=PAYMENT_METHODS, form_data=request.form)

        if not payment_method or payment_method not in PAYMENT_METHODS:
            flash('Please select a valid payment method.', 'danger')
            return render_template('add_expense.html', categories=CATEGORIES, payment_methods=PAYMENT_METHODS, form_data=request.form)

        # Create and persist expense
        try:
            new_expense = Expense(
                user_id=user_id,
                expense_name=expense_name,
                amount=amount,
                category=category,
                expense_date=expense_date,
                payment_method=payment_method,
                note=note if note else None
            )
            db.session.add(new_expense)
            db.session.commit()
            flash(f'Expense "{expense_name}" of ₹{amount:,.2f} added successfully!', 'success')
            return redirect(url_for('expense.list_expenses'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to save expense due to a database error.', 'danger')
            return render_template('add_expense.html', categories=CATEGORIES, payment_methods=PAYMENT_METHODS, form_data=request.form)

    # GET request: default date is today
    default_form = {
        'expense_date': date.today().strftime('%Y-%m-%d'),
        'payment_method': 'UPI'
    }
    return render_template('add_expense.html', categories=CATEGORIES, payment_methods=PAYMENT_METHODS, form_data=default_form)


@expense_bp.route('/edit-expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    """
    Edit an existing expense record.
    Guarantees that a user can only edit their own expenses.
    """
    user_id = session['user_id']
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        flash('Expense record not found or you are not authorized to view/edit it.', 'danger')
        return redirect(url_for('expense.list_expenses'))

    if request.method == 'POST':
        expense_name = request.form.get('expense_name', '').strip()
        amount_str = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        date_str = request.form.get('expense_date', '').strip()
        payment_method = request.form.get('payment_method', '').strip()
        note = request.form.get('note', '').strip()

        # Validation
        if not expense_name:
            flash('Expense Name cannot be blank.', 'danger')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES, payment_methods=PAYMENT_METHODS)

        try:
            amount = float(amount_str)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('edit_expense.html', expense=expense, categories=CATEGORIES, payment_methods=PAYMENT_METHODS)
        except ValueError:
            flash('Please enter a valid numeric amount.', 'danger')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES, payment_methods=PAYMENT_METHODS)

        if not category or category not in CATEGORIES:
            flash('Please select a valid expense category.', 'danger')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES, payment_methods=PAYMENT_METHODS)

        try:
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Please enter a valid date (YYYY-MM-DD).', 'danger')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES, payment_methods=PAYMENT_METHODS)

        if not payment_method or payment_method not in PAYMENT_METHODS:
            flash('Please select a valid payment method.', 'danger')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES, payment_methods=PAYMENT_METHODS)

        # Update expense attributes
        try:
            expense.expense_name = expense_name
            expense.amount = amount
            expense.category = category
            expense.expense_date = expense_date
            expense.payment_method = payment_method
            expense.note = note if note else None

            db.session.commit()
            flash('Expense record updated successfully!', 'success')
            return redirect(url_for('expense.list_expenses'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update expense due to a database error.', 'danger')
            return render_template('edit_expense.html', expense=expense, categories=CATEGORIES, payment_methods=PAYMENT_METHODS)

    return render_template('edit_expense.html', expense=expense, categories=CATEGORIES, payment_methods=PAYMENT_METHODS)


@expense_bp.route('/delete-expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    """
    Delete an expense record.
    Guarantees that a user can only delete their own expenses.
    """
    user_id = session['user_id']
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        flash('Expense record not found or you are not authorized to delete it.', 'danger')
        return redirect(url_for('expense.list_expenses'))

    try:
        expense_name = expense.expense_name
        amount = expense.amount
        db.session.delete(expense)
        db.session.commit()
        flash(f'Expense "{expense_name}" (₹{amount:,.2f}) deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete expense due to a database error.', 'danger')

    return redirect(url_for('expense.list_expenses'))
