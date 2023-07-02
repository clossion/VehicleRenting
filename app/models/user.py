from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app.models.vehicle import Vehicle

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    address_country = db.Column(db.String(64))
    address_state = db.Column(db.String(64))
    address_city = db.Column(db.String(64))
    address_detail = db.Column(db.String(256))
    user_type = db.Column(db.String(64))
    balance = db.Column(db.Float, default=0.0)  # Added this line
    vehicles = db.relationship('Vehicle', backref='seller', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
