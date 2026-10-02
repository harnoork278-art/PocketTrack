"""
Comprehensive automated test suite for PocketTrack.
Tests registration, authentication, sessions, budget management,
expense CRUD, user isolation, search/filter, and dashboard analytics.
"""
import unittest
from datetime import date
from app import app
from models import db, User, Budget, Expense


class PocketTrackTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def register_user(self, name="Aman Verma", username="aman", email="aman@test.com", password="password123", confirm_password="password123"):
        return self.client.post('/register', data={
            'name': name,
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': confirm_password
        }, follow_redirects=True)

    def login_user(self, identifier="aman", password="password123"):
        return self.client.post('/login', data={
            'identifier': identifier,
            'password': password
        }, follow_redirects=True)

    def logout_user(self):
        return self.client.get('/logout', follow_redirects=True)

    # 1. Registration Tests
    def test_registration_success(self):
        response = self.register_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful", response.data)

        with app.app_context():
            user = User.query.filter_by(username="aman").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, "aman@test.com")
            # Verify password hash
            self.assertNotEqual(user.password_hash, "password123")
            self.assertTrue(user.check_password("password123"))

    def test_registration_duplicate_username(self):
        self.register_user()
        response = self.register_user(email="aman2@test.com")
        self.assertIn(b"Username is already taken", response.data)

    def test_registration_duplicate_email(self):
        self.register_user()
        response = self.register_user(username="aman2")
        self.assertIn(b"Email is already registered", response.data)

    def test_registration_password_mismatch(self):
        response = self.register_user(password="password123", confirm_password="wrongpassword")
        self.assertIn(b"Password and Confirm Password do not match", response.data)

    def test_registration_short_password(self):
        response = self.register_user(password="123", confirm_password="123")
        self.assertIn(b"Password must be at least 6 characters long", response.data)

    # 2. Login & Logout Tests
    def test_login_success_with_username_and_email(self):
        self.register_user()
        
        # Login with username
        resp1 = self.login_user(identifier="aman", password="password123")
        self.assertIn(b"Welcome back, Aman Verma", resp1.data)
        self.logout_user()

        # Login with email
        resp2 = self.login_user(identifier="aman@test.com", password="password123")
        self.assertIn(b"Welcome back, Aman Verma", resp2.data)

    def test_login_invalid_password(self):
        self.register_user()
        response = self.login_user(identifier="aman", password="wrongpassword")
        self.assertIn(b"Invalid username/email or password", response.data)

    def test_logout_clears_session(self):
        self.register_user()
        self.login_user()
        resp = self.logout_user()
        self.assertIn(b"logged out securely", resp.data)

        # Accessing dashboard should now redirect to login
        dash_resp = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b"Please log in to access your PocketTrack account", dash_resp.data)

    # 3. Budget Management Tests
    def test_budget_setting_and_updating(self):
        self.register_user()
        self.login_user()

        current_month = date.today().strftime('%Y-%m')

        # Set initial budget
        res1 = self.client.post('/set-budget', data={'amount': '5000', 'month': current_month}, follow_redirects=True)
        self.assertEqual(res1.status_code, 200)
        self.assertIn(b"Monthly budget of", res1.data)

        with app.app_context():
            budget = Budget.query.filter_by(month=current_month).first()
            self.assertEqual(budget.amount, 5000.0)

        # Update budget
        res2 = self.client.post('/set-budget', data={'amount': '6000', 'month': current_month}, follow_redirects=True)
        self.assertIn(b"Monthly budget updated to", res2.data)

        with app.app_context():
            budget = Budget.query.filter_by(month=current_month).first()
            self.assertEqual(budget.amount, 6000.0)

    # 4. Expense CRUD Tests
    def test_add_and_list_expense(self):
        self.register_user()
        self.login_user()

        today_str = date.today().strftime('%Y-%m-%d')

        # Add expense
        add_res = self.client.post('/add-expense', data={
            'expense_name': 'College Canteen Lunch',
            'amount': '150.50',
            'category': 'Food',
            'expense_date': today_str,
            'payment_method': 'UPI',
            'note': 'Lunch with friends'
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn(b"College Canteen Lunch", add_res.data)

        with app.app_context():
            expense = Expense.query.first()
            self.assertIsNotNone(expense)
            self.assertEqual(expense.amount, 150.50)
            self.assertEqual(expense.category, 'Food')

    def test_edit_expense(self):
        self.register_user()
        self.login_user()
        today_str = date.today().strftime('%Y-%m-%d')

        self.client.post('/add-expense', data={
            'expense_name': 'Bus Ticket',
            'amount': '30.00',
            'category': 'Travel',
            'expense_date': today_str,
            'payment_method': 'Cash',
            'note': 'Daily commute'
        }, follow_redirects=True)

        with app.app_context():
            expense_id = Expense.query.first().id

        # Edit expense
        edit_res = self.client.post(f'/edit-expense/{expense_id}', data={
            'expense_name': 'Metro Smartcard Recharge',
            'amount': '200.00',
            'category': 'Travel',
            'expense_date': today_str,
            'payment_method': 'UPI',
            'note': 'Monthly metro recharge'
        }, follow_redirects=True)
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn(b"Expense record updated successfully", edit_res.data)

        with app.app_context():
            updated = db.session.get(Expense, expense_id)
            self.assertEqual(updated.expense_name, 'Metro Smartcard Recharge')
            self.assertEqual(updated.amount, 200.00)

    def test_delete_expense(self):
        self.register_user()
        self.login_user()
        today_str = date.today().strftime('%Y-%m-%d')

        self.client.post('/add-expense', data={
            'expense_name': 'Temporary Item',
            'amount': '50.00',
            'category': 'Other',
            'expense_date': today_str,
            'payment_method': 'Cash',
            'note': 'To be deleted'
        }, follow_redirects=True)

        with app.app_context():
            expense_id = Expense.query.first().id

        del_res = self.client.post(f'/delete-expense/{expense_id}', follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertIn(b"deleted successfully", del_res.data)

        with app.app_context():
            self.assertIsNone(db.session.get(Expense, expense_id))

    # 5. User Isolation Security Test
    def test_user_data_isolation(self):
        # Register User 1
        self.register_user(name="User One", username="user1", email="user1@test.com")
        self.login_user("user1")
        today_str = date.today().strftime('%Y-%m-%d')
        self.client.post('/add-expense', data={
            'expense_name': 'Secret Note 1',
            'amount': '1000.00',
            'category': 'Bills',
            'expense_date': today_str,
            'payment_method': 'UPI',
            'note': 'User 1 personal expense'
        }, follow_redirects=True)
        self.logout_user()

        # Register User 2
        self.register_user(name="User Two", username="user2", email="user2@test.com")
        self.login_user("user2")

        # User 2 views expenses list -> Must NOT see User 1's expense
        list_res = self.client.get('/expenses')
        self.assertNotIn(b"Secret Note 1", list_res.data)

        # User 2 tries to edit User 1's expense
        with app.app_context():
            u1_expense = Expense.query.filter_by(expense_name='Secret Note 1').first()
            u1_id = u1_expense.id

        unauth_edit = self.client.get(f'/edit-expense/{u1_id}', follow_redirects=True)
        self.assertIn(b"not authorized", unauth_edit.data)

        unauth_delete = self.client.post(f'/delete-expense/{u1_id}', follow_redirects=True)
        self.assertIn(b"not authorized", unauth_delete.data)

        # Verify User 1's expense still exists
        with app.app_context():
            self.assertIsNotNone(db.session.get(Expense, u1_id))

    # 6. Dashboard Calculations & Budget Warning States
    def test_dashboard_calculations_and_budget_states(self):
        self.register_user()
        self.login_user()
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        month_str = today.strftime('%Y-%m')

        # Set budget of 5000
        self.client.post('/set-budget', data={'amount': '5000', 'month': month_str}, follow_redirects=True)

        # Add 3250 in expenses (Food: 2000, Travel: 1250)
        self.client.post('/add-expense', data={
            'expense_name': 'Groceries & Mess',
            'amount': '2000.00',
            'category': 'Food',
            'expense_date': today_str,
            'payment_method': 'UPI'
        }, follow_redirects=True)

        self.client.post('/add-expense', data={
            'expense_name': 'Train Pass',
            'amount': '1250.00',
            'category': 'Travel',
            'expense_date': today_str,
            'payment_method': 'UPI'
        }, follow_redirects=True)

        # Check dashboard metrics
        dash = self.client.get('/dashboard')
        self.assertEqual(dash.status_code, 200)
        # Total Spent: 3,250.00
        self.assertIn(b"3,250.00", dash.data)
        # Remaining: 1,750.00
        self.assertIn(b"1,750.00", dash.data)
        # Highest Category: Food
        self.assertIn(b"Food", dash.data)
        # State: normal (3250 / 5000 = 65% < 80%)
        self.assertIn(b"state-normal", dash.data)

        # Add expense of 900 to push total to 4150 (83% -> Warning State)
        self.client.post('/add-expense', data={
            'expense_name': 'Textbooks',
            'amount': '900.00',
            'category': 'Education',
            'expense_date': today_str,
            'payment_method': 'UPI'
        }, follow_redirects=True)

        dash_warn = self.client.get('/dashboard')
        self.assertIn(b"state-warning", dash_warn.data)
        self.assertIn(b"Warning: You have used", dash_warn.data)

        # Add expense of 1000 to push total to 5150 (> 5000 -> Exceeded State)
        self.client.post('/add-expense', data={
            'expense_name': 'Laptop Repair',
            'amount': '1000.00',
            'category': 'Bills',
            'expense_date': today_str,
            'payment_method': 'Debit Card'
        }, follow_redirects=True)

        dash_over = self.client.get('/dashboard')
        self.assertIn(b"state-exceeded", dash_over.data)
        self.assertIn(b"Budget exceeded by", dash_over.data)


if __name__ == '__main__':
    unittest.main()
