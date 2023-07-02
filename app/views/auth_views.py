from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user
from app import app, db
from app.forms.user_forms import LoginForm, RegistrationForm
from app.models.user import User

@app.route('/')
def index():
    return redirect(url_for('login'))  # redirect to login page by default

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        if form.login_as.data != user.user_type and form.login_as.data == 'seller':
            flash('You are not a seller. Please login as a buyer.')
            return redirect(url_for('login'))
        login_user(user)
        # 根据用户类型重定向到不同的页面
        if form.login_as.data == 'buyer':
            return redirect(url_for('buyer'))
        else:
            return redirect(url_for('seller'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(user_type=form.user_type.data, username=form.username.data, email=form.email.data, phone=form.phone.data,
                    address_country=form.address_country.data, address_state=form.address_state.data,
                    address_city=form.address_city.data, address_detail=form.address_detail.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))  # redirect to login page after logout
