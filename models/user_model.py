"""
User model for PocketTrack authentication and profile management.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db


class User(db.Model):
    """
    User entity representing registered students in PocketTrack.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships: Deleting a user cascades and removes their budgets and expenses
    budgets = db.relationship('Budget', backref='user', cascade='all, delete-orphan', lazy=True)
    expenses = db.relationship('Expense', backref='user', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password: str):
        """Hashes the user password using Werkzeug's secure hash algorithm."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies candidate password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"
