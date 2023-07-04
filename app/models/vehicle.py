# vehicle.py
from app import db
from flask import url_for

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # assuming the user model is in the same package
    brand = db.Column(db.String(120))
    model = db.Column(db.String(120))
    price_per_day = db.Column(db.Float)
    location = db.Column(db.String(120))
    delivery_option = db.Column(db.Boolean)
    same_city_return_option = db.Column(db.Boolean)
    long_term_discount_option = db.Column(db.Boolean)
    photo = db.Column(db.String(120))
    vehicle_id = db.Column(db.String(120))
    license_plate = db.Column(db.String(120))
    color = db.Column(db.String(120))
    displacement = db.Column(db.Float)
    mileage = db.Column(db.Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_dict(self):
        return {
            'id': self.id,
            'brand': self.brand,
            'model': self.model,
            'price_per_day': self.price_per_day,  # Add this line
            'photo_url': url_for('static', filename='images/' + self.photo),
        }


