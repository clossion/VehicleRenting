# vehicle_views.py
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app import app, db
from app.models import User
from app.models.vehicle import Vehicle
from app.models.order import Order
from app.forms.vehicle_form import VehicleForm
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
from datetime import datetime
import random
import string
from pypinyin import lazy_pinyin
import base64

def calculate_total_price(price_per_day, start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    num_days = (end_date - start_date).days + 1
    return price_per_day * num_days


@app.template_filter('b64decode')
def base64_decode(value):
    if value is not None:
        return f"data:image/jpeg;base64,{value}"
    return value

@app.route('/vehicles/filter', methods=['GET'])
def filter_vehicles():
    letter = request.args.get('letter')
    brand = request.args.get('brand')
    model = request.args.get('model')

    if letter and brand:
        all_vehicles = Vehicle.query.all()
        vehicles = [vehicle for vehicle in all_vehicles if lazy_pinyin(vehicle.brand)[0][0].lower() == letter.lower() and vehicle.brand == brand]
    elif letter:
        all_vehicles = Vehicle.query.all()
        vehicles = [vehicle for vehicle in all_vehicles if lazy_pinyin(vehicle.brand)[0][0].lower() == letter.lower()]
    elif brand and model:
        vehicles = Vehicle.query.filter_by(brand=brand, model=model).all()
    else:
        vehicles = Vehicle.query.all()

    return jsonify([vehicle.to_dict() for vehicle in vehicles])

@app.route('/vehicles/filter_by_letter/<letter>', methods=['GET'])
def filter_vehicles_by_letter(letter):
    all_vehicles = Vehicle.query.all()
    vehicles = [vehicle for vehicle in all_vehicles if lazy_pinyin(vehicle.brand)[0][0].lower() == letter.lower()]
    return jsonify([vehicle.to_dict() for vehicle in vehicles])

@app.route('/vehicles/filter_by_brand/<brand>', methods=['GET'])
def filter_vehicles_by_brand(brand):
    vehicles = Vehicle.query.filter_by(brand=brand).all()
    return jsonify([vehicle.to_dict() for vehicle in vehicles])


@app.route('/brands/<letter>', methods=['GET'])
def get_brands(letter):
    all_vehicles = Vehicle.query.all()
    brands = set(vehicle.brand for vehicle in all_vehicles if lazy_pinyin(vehicle.brand)[0][0].lower() == letter.lower())
    return jsonify(list(brands))

@app.route('/models/<brand>', methods=['GET'])
def get_models(brand):
    all_vehicles = Vehicle.query.all()
    models = set(vehicle.model for vehicle in all_vehicles if vehicle.brand == brand)
    return jsonify(list(models))

@app.route('/post_vehicle', methods=['GET', 'POST'])
@login_required
def post_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        path = os.path.join(app.root_path, 'static/images/', filename)
        f.save(path)
        vehicle = Vehicle(seller_id=current_user.id,
                          brand=form.brand.data,
                          model=form.model.data,
                          license_plate=form.license_plate.data,
                          color=form.color.data,
                          displacement=form.displacement.data,
                          mileage=form.mileage.data,
                          price_per_day=form.price_per_day.data,
                          location=form.location.data,
                          delivery_option=form.delivery_option.data,
                          same_city_return_option=form.same_city_return_option.data,
                          long_term_discount_option=form.long_term_discount_option.data,
                          photo=os.path.basename(path))

        db.session.add(vehicle)
        db.session.commit()
        flash('Your vehicle has been posted!', 'success')
        return redirect(url_for('seller'))
    return render_template('post_vehicle.html', title='Post Vehicle', form=form)

@app.route('/edit_vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.seller_id != current_user.id:
        abort(403)
    form = VehicleForm(obj=vehicle)
    if form.validate_on_submit():
        # Handle the photo upload
        if form.photo.data:
            f = form.photo.data
            if isinstance(f, FileStorage):
                filename = secure_filename(f.filename)
                path = os.path.join(app.root_path, 'static/images/', filename)
                f.save(path)
                form.photo.data = filename  # Set the form data to the filename
        form.populate_obj(vehicle)
        db.session.commit()
        flash('Vehicle information has been updated.')
        return redirect(url_for('seller'))
    return render_template('edit_vehicle.html', form=form)


@app.route('/delete_vehicle/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.seller_id != current_user.id:
        abort(403)  # Forbidden, the current user is not the seller of this vehicle
    db.session.delete(vehicle)
    db.session.commit()
    flash('Your vehicle has been deleted!', 'success')
    return redirect(url_for('seller'))

@app.route('/rent_vehicle/<int:vehicle_id>', methods=['GET'])
@login_required
def rent_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return render_template('rent_vehicle.html', vehicle=vehicle)

from flask import session
from app.models.rental import Rental

@app.route('/confirm_rental/<int:vehicle_id>', methods=['POST'])
@login_required
def confirm_rental(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    total_price = calculate_total_price(vehicle.price_per_day, start_date, end_date)
    rental = Rental(vehicle_id=vehicle.id, user_id=current_user.id, start_date=start_date, end_date=end_date, total_price=total_price)

    db.session.add(rental)
    db.session.commit()

    session['rental_id'] = rental.id

    return redirect(url_for('payment_confirmation', rental_id=rental.id))

@app.route('/payment_confirmation', methods=['GET', 'POST'])
@login_required
def payment_confirmation():
    rental_id = session.get('rental_id')
    if rental_id is None:
        abort(404)  # No rental id in session, something went wrong
    rental = Rental.query.get_or_404(rental_id)
    vehicle = rental.vehicle  # Get the vehicle from the rental

    # Get the existing order if it exists
    order = Order.query.filter_by(buyer_id=current_user.id, vehicle_id=vehicle.id, status='Unpaid').first()

    if request.method == 'POST':
        # Handle payment here
        if order is None:
            order = Order(buyer_id=current_user.id, seller_id=vehicle.seller_id, vehicle_id=vehicle.id,
                          start_date=rental.start_date, end_date=rental.end_date, total_price=rental.total_price,
                          status='Unpaid')
            db.session.add(order)
        if current_user.balance < rental.total_price:
            flash('Your balance is not enough to pay for this vehicle.', 'error')
            order.status = 'Unpaid'  # Set the order status to 'Unpaid'
            db.session.commit()  # Commit the changes to the database
            return redirect(url_for('buyer_orders', rental_id=rental.id))  # Use rental_id instead of vehicle_id
        current_user.balance -= order.total_price
        order.verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        order.status = 'Paid'
        db.session.commit()
        flash('Payment successful!', 'success')
        return redirect(url_for('buyer'))

    total_cost = rental.total_price  # Calculate the total cost
    return render_template('payment_confirmation.html', rental=rental, total_cost=total_cost, order=order)

# 在 app/views/vehicle_views.py 文件中的一个新的视图函数中

@app.route('/verify_order/<int:order_id>', methods=['POST'])
@login_required
def verify_order(order_id):
    order = Order.query.get_or_404(order_id)

    # 检查当前用户是否是订单的卖家
    if current_user.id != order.seller_id:
        abort(403)

    # 检查验证码是否正确
    if request.form['verification_code'] != order.verification_code:
        flash('The verification code is incorrect.', 'error')
        return redirect(url_for('seller_orders'))

    # 验证码正确，将订单的金额转到卖家的账户上
    seller = User.query.get(order.seller_id)
    seller.balance += order.total_price

    # 更新订单的状态
    order.status = 'Completed'

    db.session.commit()

    flash('Order verified successfully!', 'success')
    return redirect(url_for('seller_orders'))

@app.route('/order_confirmation/<int:rental_id>', methods=['GET'])
@login_required
def order_confirmation(rental_id):
    order = Order.query.get(rental_id)
    if order is None:
        abort(404)
    return render_template('order_confirmation.html', order=order)

@app.route('/cancel_payment', methods=['POST'])
@login_required
def cancel_payment():
    rental_id = session.get('rental_id')
    if rental_id is None:
        abort(404)  # No rental id in session, something went wrong
    rental = Rental.query.get_or_404(rental_id)
    order = Order.query.filter_by(buyer_id=current_user.id, vehicle_id=rental.vehicle_id, status='Unpaid').first()
    if order is not None:
        db.session.delete(order)
        db.session.commit()
    return redirect(url_for('buyer'))


