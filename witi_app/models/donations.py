# from witi_app import db
# from datetime import datetime

# class Donation(db.Model):
#     __tablename__ = 'donations'
#     id = db.Column(db.Integer, primary_key=True)
#     donor_name = db.Column(db.String(100), nullable=False)
#     donor_email = db.Column(db.String(100), nullable=False)
#     donation_amount = db.Column(db.Float, nullable=False)
#     donation_date = db.Column(db.DateTime, default=datetime.now())
#     message = db.Column(db.Text, nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.now())
#     updated_at = db.Column(db.DateTime, onupdate=datetime.now())

#     def __init__(self, donor_name, donor_email, donation_amount, message=None):
#         self.donor_name = donor_name
#         self.donor_email = donor_email
#         self.donation_amount = donation_amount
#         self.message = message

#     def __repr__(self):
#         return f"Donation('{self.donor_name}', '{self.donation_amount}')"

from witi_app import db
from datetime import datetime

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(100), nullable=False)
    donor_email = db.Column(db.String(100), nullable=False)
    donation_amount_usd = db.Column(db.Float, nullable=True)
    donation_amount_ugx = db.Column(db.Float, nullable=True)
    payment_method = db.Column(db.String(50), nullable=False)
    screenshot_path = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=True)
    donation_date = db.Column(db.DateTime, default=datetime.now())
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, donor_name, donor_email, donation_amount_usd=None, donation_amount_ugx=None, payment_method="", screenshot_path=None, message=None):
        self.donor_name = donor_name
        self.donor_email = donor_email
        self.donation_amount_usd = donation_amount_usd
        self.donation_amount_ugx = donation_amount_ugx
        self.payment_method = payment_method
        self.screenshot_path = screenshot_path
        self.message = message

    def __repr__(self):
        return f"Donation('{self.donor_name}', '{self.donation_amount_usd if self.donation_amount_usd else self.donation_amount_ugx}')"
