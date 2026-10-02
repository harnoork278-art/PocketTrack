"""
Seed script for PocketTrack.
Creates a demo student account with realistic expenses and budget
for demonstration and academic evaluation.
"""
from datetime import date, timedelta
from app import app
from models import db, User, Budget, Expense


def seed_data():
    with app.app_context():
        # Check if demo student exists
        existing_student = User.query.filter_by(username='rahul').first()
        if existing_student:
            print("Demo student 'rahul' already exists. Skipping seed.")
            return

        print("Seeding demo student account...")
        student = User(
            name="Rahul Sharma",
            username="rahul",
            email="rahul@college.edu"
        )
        student.set_password("student123")
        db.session.add(student)
        db.session.commit()

        # Set current month budget
        today = date.today()
        month_str = today.strftime('%Y-%m')
        budget = Budget(
            user_id=student.id,
            month=month_str,
            amount=5000.00
        )
        db.session.add(budget)

        # Seed sample expenses
        sample_expenses = [
            ("College Canteen Lunch & Snacks", 120.00, "Food", today - timedelta(days=1), "UPI", "Split with Rohan"),
            ("Database Systems Textbook", 450.00, "Education", today - timedelta(days=2), "Debit Card", "BCA Sem 4 text"),
            ("Monthly City Bus Pass", 600.00, "Travel", today - timedelta(days=4), "Cash", "Route 24 Pass"),
            ("Mobile Recharge 28 Days", 299.00, "Bills", today - timedelta(days=6), "UPI", "Jio Unlimited Pack"),
            ("Weekend Movie Ticket", 350.00, "Entertainment", today - timedelta(days=7), "UPI", "PVR Cinemas"),
            ("Assignment Spiral Binding", 85.00, "Education", today - timedelta(days=8), "Cash", "Java project reports"),
            ("Hostel Mess Advance", 1500.00, "Food", today - timedelta(days=10), "UPI", "Monthly food token"),
            ("Pharmacy Medicine", 180.00, "Health", today - timedelta(days=12), "Cash", "Cold & fever medicine"),
        ]

        for name, amount, cat, exp_date, pay_method, note in sample_expenses:
            expense = Expense(
                user_id=student.id,
                expense_name=name,
                amount=amount,
                category=cat,
                expense_date=exp_date,
                payment_method=pay_method,
                note=note
            )
            db.session.add(expense)

        db.session.commit()
        print("Demo data seeded successfully!")
        print("Login credentials:")
        print("  Username: rahul (or email: rahul@college.edu)")
        print("  Password: student123")


if __name__ == '__main__':
    seed_data()
