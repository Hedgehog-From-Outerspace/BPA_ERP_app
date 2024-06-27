from flask import Blueprint, render_template, request, flash, jsonify
from .models import Order, SupplyOrder, Record, Stock
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

@views.route('/accountmanager', methods=['GET', 'POST'])
def accountmanager():
    client_timezone = pytz.timezone('Europe/Amsterdam')
    today = datetime.now(timezone.utc).date()
    
    # Query records for orders created today
    records_created = Record.query.filter(
        db.func.date(Record.date_time) == today,
        Record.activity == "Order created"
    ).all()
    
    # Query records for orders finished today
    records_finished = Record.query.filter(
        db.func.date(Record.date_time) == today,
        Record.activity == "Order finished"
    ).all()
    
    # Extract order ids from both "Order created" and "Order finished" records
    order_ids_created = [record.OrderId for record in records_created]
    order_ids_finished = [record.OrderId for record in records_finished]
    
    # Query orders based on extracted order ids
    orders_created = Order.query.filter(Order.id.in_(order_ids_created)).all()
    orders_finished = Order.query.filter(Order.id.in_(order_ids_finished)).all()
    
    # Create dictionaries to map order ids to their respective dates
    order_dates_created = {
        record.OrderId: (
            record.date_time.replace(tzinfo=pytz.utc).astimezone(client_timezone).strftime('%Y-%m-%d %H:%M'),
            record.period
        ) for record in records_created
    }
    
    order_dates_finished = {
        record.OrderId: record.period for record in records_finished
    }
    
    # Render the template with orders and order_dates
    return render_template("accountmanager.html", 
                           orders_created=orders_created, 
                           order_dates_created=order_dates_created,
                           order_dates_finished=order_dates_finished)


@views.route('/voorraadbeheer', methods=['GET', 'POST'])
def inventorykmanagement():
    client_timezone = pytz.timezone('Europe/Amsterdam')
    if request.method == 'POST':
        pass

    # get stock
    stock = Stock.query.first()

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

    return render_template("inventorymanager.html", orders=orders, order_dates=order_dates, stock=stock)

@views.route('/leverancier', methods=['GET', 'POST'])
def supplier():
    return render_template("supplier.html")

@views.route('/productie', methods=['GET', 'POST'])
def production():
    return render_template("production.html")

@views.route('/update_order_status', methods=['POST'])
def update_order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    correct = data.get('correct')
    type = data.get('type')
    actual_delivery_period = data.get('actual_delivery_period')

    order = Order.query.get(order_id)
    if order:
        if type == 'customer':
            order.customer_checked = correct
            if correct:
                create_record(order.id, -1, "Customer approved order")
            else:
                create_record(order.id, -1, "Customer disapproved order")
        elif type == 'accountmanager':
            order.accountmanager_checked = correct
            if correct:
                create_record(order.id, -1, "Account manager approved order")
            else:
                create_record(order.id, -1, "Account manager disapproved order")
        else:
            return jsonify({'error': 'Invalid type provided'}), 400

        if correct and type == 'accountmanager' and actual_delivery_period is not None:
            try:
                actual_delivery_period = int(actual_delivery_period)
                # Create a new record for "Order finished"
                create_record(order.id, actual_delivery_period, "Order finished")
            except ValueError:
                return jsonify({'error': 'Invalid actual delivery period provided'}), 400

        # Commit the changes
        db.session.commit()

        return jsonify({'message': 'Order status updated successfully'}), 200
    else:
        return jsonify({'error': 'Order not found'}), 404


def create_record(order_id, period, activity):
    new_record = Record(OrderId=order_id, period=period, activity=activity)
    db.session.add(new_record)
