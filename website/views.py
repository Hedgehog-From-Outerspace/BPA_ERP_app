from flask import Blueprint, render_template, request, flash, jsonify
from .models import Order, SupplyOrder, Record
from . import db
from datetime import datetime, timezone
import os
import pytz

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/klant', methods=['GET', 'POST'])
def customer():
    client_timezone = pytz.timezone('Europe/Amsterdam')
    if request.method == 'POST':
        period = request.form.get('period')
        item_type = request.form.get('type').upper()
        amount = request.form.get('amount')

        if item_type.lower() not in ['a', 'b', 'c']:
            flash("Invalid item type", category='error')
        else:
            new_order = Order(item_type=item_type, amount=amount)
            db.session.add(new_order)
            db.session.commit()

            newRecord = Record(OrderId=new_order.id, period=period, activity="Order created")
            db.session.add(newRecord)
            db.session.commit()
            flash("Bestelling geplaatst", category='success')

    today = datetime.now(timezone.utc).date()
    records = Record.query.filter(
        db.func.date(Record.date_time) == today, 
        Record.activity == "Order created"
    ).all()
    order_ids = [record.OrderId for record in records]
    orders = Order.query.filter(Order.id.in_(order_ids)).all()

    # Create a dictionary to map order ids to their "Order created" dates
    order_dates = {
        record.OrderId: (
            record.date_time.replace(tzinfo=pytz.utc).astimezone(client_timezone).strftime('%Y-%m-%d %H:%M'),
            record.period
        ) for record in records
    }

    return render_template("customer.html", orders=orders, order_dates=order_dates)

@views.route('/update_order_status', methods=['POST'])
def update_order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    correct = data.get('correct')
    type = data.get('type')

    order = Order.query.get(order_id)
    if order:
        if type == 'customer':
            order.customer_checked = correct
            activity = "Customer approved order"
        elif type == 'accountmanager':
            order.accountmanager_checked = correct
            activity = "Account manager approved order"
        else:
            return jsonify({'error': 'Invalid type provided'}), 400

        # Create a new record for the activity
        new_record = Record(OrderId=order.id, period=-1, activity=activity)
        db.session.add(new_record)
        db.session.commit()

        return jsonify({'message': 'Order status updated successfully'}), 200
    else:
        return jsonify({'error': 'Order not found'}), 404

@views.route('/accountmanager', methods=['GET', 'POST'])
def accountmanager():
    client_timezone = pytz.timezone('Europe/Amsterdam')
    if request.method == 'POST':
        True
    
    # get all orders
    today = datetime.now(timezone.utc).date()
    records = Record.query.filter(
        db.func.date(Record.date_time) == today, 
        Record.activity == "Order created"
    ).all()
    order_ids = [record.OrderId for record in records]
    orders = Order.query.filter(Order.id.in_(order_ids)).all()

    # Create a dictionary to map order ids to their "Order created" dates
    order_dates = {
        record.OrderId: (
            record.date_time.replace(tzinfo=pytz.utc).astimezone(client_timezone).strftime('%Y-%m-%d %H:%M'),
            record.period
        ) for record in records
    }
    return render_template("accountmanager.html", orders=orders, order_dates=order_dates)

@views.route('/voorraadbeheer', methods=['GET', 'POST'])
def inventorykmanagement():
    return render_template("inventorymanager.html")

@views.route('/leverancier', methods=['GET', 'POST'])
def supplier():
    return render_template("supplier.html")

@views.route('/productie', methods=['GET', 'POST'])
def production():
    return render_template("production.html")
