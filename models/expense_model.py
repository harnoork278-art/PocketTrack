"""
Expense model for storing student expenditures in PocketTrack.
"""
from datetime import datetime, date
from models.database import db


class Expense(db.Model):
    """
    Expense entity representing an individual spending transaction by a student.
    """
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    expense_name = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(50), nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Expense id={self.id} user_id={self.user_id} name={self.expense_name} amount={self.amount}>"
