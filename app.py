"""
PocketTrack – Student Expense & Budget Manager
Main Flask Application Entrypoint
Follows MVC Architecture (Model - View - Controller)
"""
import os
from flask import Flask, render_template, session
from models.database import db
from models.user_model import User
from models.budget_model import Budget
from models.expense_model import Expense
from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.expense_controller import expense_bp

# Determine base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Ensure database directory exists
db_dir = os.path.join(basedir, 'database')
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, 'pockettrack.db')

# Initialize Flask application with MVC view and static configurations
app = Flask(
    __name__,
    template_folder='views',
    static_folder='static'
)

# Application Configurations
app.config['SECRET_KEY'] = 'pockettrack-bca-academic-secure-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)

# Register Controller Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(expense_bp)


# Context processor to make logged-in student info accessible in all Jinja views
@app.context_processor
def inject_global_data():
    current_user = None
    if 'user_id' in session:
        current_user = db.session.get(User, session['user_id'])
    return dict(current_user=current_user)


# Custom Jinja filters
@app.template_filter('currency')
def currency_filter(value):
    """Formats a number into Indian Rupee representation."""
    try:
        val = float(value)
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return f"₹0.00"


# Global Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('dashboard.html', error_title="404 - Page Not Found",
                           error_message="The requested page does not exist."), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('dashboard.html', error_title="500 - Server Error",
                           error_message="An internal server error occurred."), 500


# Create tables on application initialization
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    # Run development server on http://127.0.0.1:5000
    app.run(debug=True, host='127.0.0.1', port=5000)
