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
    photo = db.Column(db.String(120))  # change this line
    vehicle_id = db.Column(db.String(120))  # new field
    license_plate = db.Column(db.String(120))  # new field
    color = db.Column(db.String(120))  # new field
    displacement = db.Column(db.Float)  # new field
    mileage = db.Column(db.Float)  # new field

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_dict(self):
        return {
            'id': self.id,
            'brand': self.brand,
            'model': self.model,
            'photo_url': url_for('static', filename='images/' + self.photo),
            # ... other fields ...
        }

