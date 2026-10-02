"""
Controllers package initialization.
"""
from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.expense_controller import expense_bp

__all__ = ['auth_bp', 'dashboard_bp', 'expense_bp']
