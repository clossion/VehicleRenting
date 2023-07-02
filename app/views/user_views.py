from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import app, db
from app.forms.user_forms import UpdateForm
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.order import Order

@app.route('/personal', methods=['GET', 'POST'])
@login_required
def personal():
    form = UpdateForm(obj=current_user)
    if form.validate_on_submit():
        if form.submit.data:
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.phone = form.phone.data
            current_user.address_country = form.address_country.data
            current_user.address_state = form.address_state.data
            current_user.address_city = form.address_city.data
            current_user.address_detail = form.address_detail.data
            db.session.commit()
            flash('Your information has been updated.')
            if current_user.user_type == 'seller':
                return redirect(url_for('seller'))
            else:
                return redirect(url_for('buyer'))
    return render_template('personal.html', form=form)


@app.route('/buyer')
@login_required
def buyer():
    vehicles = Vehicle.query.all()  # Query all vehicles
    orders = Order.query.filter_by(seller_id=current_user.id).all()
    return render_template('buyer.html', title='Buyer', vehicles=vehicles, orders=orders)


@app.route('/seller')
@login_required
def seller():
    vehicles = current_user.vehicles.filter_by(seller_id = current_user.id).all()
    orders = Order.query.filter_by(seller_id=current_user.id).all()
    return render_template('seller.html', vehicles=vehicles, orders=orders)

@app.route('/buyer_orders')
@login_required
def buyer_orders():
    orders = Order.query.filter_by(buyer_id=current_user.id).all()
    return render_template('buyer_orders.html', orders=orders)

@app.route('/seller_orders')
@login_required
def seller_orders():
    orders = Order.query.filter_by(seller_id=current_user.id).all()
    return render_template('seller_orders.html', orders=orders)
