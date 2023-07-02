# vehicle_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
from flask_wtf.file import FileField, FileAllowed

class VehicleForm(FlaskForm):
    vehicle_id = StringField('Vehicle ID', validators=[DataRequired()])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png']), Optional()])
    brand = StringField('Brand', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    license_plate = StringField('License Plate', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired()])
    displacement = FloatField('Displacement', validators=[DataRequired()])
    mileage = FloatField('Mileage', validators=[DataRequired()])
    price_per_day = FloatField('Price per Day', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    delivery_option = BooleanField('Delivery Available')
    same_city_return_option = BooleanField('Same City Return Available')
    long_term_discount_option = BooleanField('Long Term Discount Available')
    submit = SubmitField('Submit')
    photo_file = FileField('Vehicle Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])