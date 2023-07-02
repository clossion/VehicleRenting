from app import db
import random
import string
from sqlalchemy.orm import relationship

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(64))
    verification_code = db.Column(db.String(10))
    seller = db.relationship('User', backref='sales', foreign_keys=[seller_id])
    vehicle = db.relationship('Vehicle', backref='orders')
    # Add any other fields you need for your order
    buyer = db.relationship('User', backref='buyer_orders', foreign_keys=[buyer_id])
    seller = db.relationship('User', backref='seller_orders', foreign_keys=[seller_id])

    def __init__(self, buyer_id, seller_id, vehicle_id, start_date, end_date, total_price, status):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.vehicle_id = vehicle_id
        self.start_date = start_date
        self.end_date = end_date
        self.total_price = total_price
        self.status = status


