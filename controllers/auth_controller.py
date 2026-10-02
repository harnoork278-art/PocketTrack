"""
Authentication controller for PocketTrack.
Handles student registration, login, session management, and logout.
"""
import re
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """
    Decorator to ensure routes are only accessible to authenticated users.
    Redirects unauthenticated visitors to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access your PocketTrack account.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def is_valid_email(email: str) -> bool:
    """Validate email address format using regular expression."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new student user registration."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic field validation
        if not name or not username or not email or not password or not confirm_password:
            flash('All registration fields are required.', 'danger')
            return render_template('register.html', form_data=request.form)

        if len(name) < 2:
            flash('Full Name must be at least 2 characters long.', 'danger')
            return render_template('register.html', form_data=request.form)

        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
            flash('Username must be 3-30 characters and contain only letters, numbers, and underscores.', 'danger')
            return render_template('register.html', form_data=request.form)

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html', form_data=request.form)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', form_data=request.form)

        if password != confirm_password:
            flash('Password and Confirm Password do not match.', 'danger')
            return render_template('register.html', form_data=request.form)

        # Check for unique username and email in SQLite database
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('register.html', form_data=request.form)

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email is already registered. Please log in or use a different email.', 'danger')
            return render_template('register.html', form_data=request.form)

        # Create new user record with hashed password
        try:
            new_user = User(name=name, username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! You can now log in with your credentials.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html', form_data=request.form)

    return render_template('register.html', form_data={})


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle student user authentication and session establishment."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip().lower()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash('Please provide both username/email and password.', 'danger')
            return render_template('login.html', identifier=identifier)

        # Query user by username or email
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['username'] = user.username
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')
            return render_template('login.html', identifier=identifier)

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Clear student session and redirect to login page."""
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))
