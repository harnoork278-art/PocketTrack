"""
Budget model for monthly budget tracking in PocketTrack.
"""
from datetime import datetime
from models.database import db


class Budget(db.Model):
    """
    Budget entity storing monthly budget allocations for a specific user.
    """
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    month = db.Column(db.String(7), nullable=False)  # Format: 'YYYY-MM'
    amount = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Budget user_id={self.user_id} month={self.month} amount={self.amount}>"
