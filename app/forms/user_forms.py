from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User
from flask_login import current_user
import phonenumbers
import pycountry

# 电话号码验证器
from phonenumbers import carrier

from phonenumbers import phonenumberutil

def validate_phone(form, field):
    # List of country codes for countries that do not distinguish between mobile and landline numbers
    no_mobile_landline_distinction_countries = ['US', 'CA']

    try:
        # Get the country object of the selected country
        selected_country_obj = pycountry.countries.get(alpha_2=form.address_country.data)
        if selected_country_obj is None:
            raise ValidationError(f'无效的国家代码: {form.address_country.data}')
        selected_country = selected_country_obj.alpha_2
        # If the phone number does not start with the country code of the selected country, add the country code to the phone number
        if not field.data.startswith(selected_country):
            field.data = selected_country + field.data
        # Parse the phone number with the default country code
        parsed_number = phonenumbers.parse(field.data, selected_country)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError('号码有误')
        # Get the country code of the phone number
        phone_country_code = phonenumbers.region_code_for_number(parsed_number)
        # Get the country object of the phone number
        phone_country = pycountry.countries.get(alpha_2=phone_country_code)
        if phone_country is None:
            raise ValidationError(f'无效的电话号码国家代码: {phone_country_code}')
        # Check if the phone country matches the selected country
        if selected_country != phone_country_code:
            raise ValidationError('电话号码与所选国家不匹配')
        # Check if the phone number is a mobile number, but only if the country distinguishes between mobile and landline numbers
        if selected_country not in no_mobile_landline_distinction_countries:
            carrier_name = carrier.name_for_number(parsed_number, 'en')
            if 'mobile' not in carrier_name.lower():
                raise ValidationError('请输入移动电话号码')
        print(f"Phone country: {phone_country.name}")
    except phonenumbers.NumberParseException:
        raise ValidationError('Invalid phone number.')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20, message="Username must be between 3 and 20 characters long")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20, message="Password must be between 6 and 20 characters long")])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    phone = StringField('Phone', validators=[DataRequired(), validate_phone])
    address_country = SelectField('Country',
                                  choices=[(country.alpha_2, country.name) for country in pycountry.countries],
                                  validators=[DataRequired()])
    address_state = StringField('State', validators=[DataRequired()])
    address_city = StringField('City', validators=[DataRequired()])
    address_detail = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Register')
    user_type = SelectField('User Type', choices=[('buyer', 'Buyer'), ('seller', 'Seller')],
                            validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20, message="Username must be between 3 and 20 characters long")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20, message="Password must be between 6 and 20 characters long")])
    login_as = SelectField('Login As', choices=[('buyer', 'Buyer'), ('seller', 'Seller')],
                            validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20, message="Username must be between 3 and 20 characters long")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), validate_phone])
    address_country = SelectField('Country',
                                  choices=[(country.alpha_2, country.name) for country in pycountry.countries],
                                  validators=[DataRequired()])
    address_state = StringField('State', validators=[DataRequired()])
    address_city = StringField('City', validators=[DataRequired()])
    address_detail = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Update')
    cancel = SubmitField('Cancel')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')
