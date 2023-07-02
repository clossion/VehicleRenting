from app import db
from app.models.user import User
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# rental.py
class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    renter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    user = relationship('User', backref='rentals', foreign_keys=[renter_id])
    total_price = db.Column(db.Float)
    vehicle = db.relationship('Vehicle', backref='rentals')