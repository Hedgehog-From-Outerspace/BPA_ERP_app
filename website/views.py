from flask import Blueprint, render_template, request, flash, jsonify
from .models import Order, SupplyOrder, Record, Stock
from . import db
from datetime import datetime, timezone
import os
import pytz

views = Blueprint('views', __name__)

order_specifications = {
    'A': {'blue': 3, 'red': 4, 'grey': 2},
    'B': {'blue': 2, 'red': 2, 'grey': 4},
    'C': {'blue': 3, 'red': 3, 'grey': 2}
}

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/klant', methods=['GET', 'POST'])
def customer():
    client_timezone = pytz.timezone('Europe/Amsterdam')
    today = datetime.now(timezone.utc).date()

    if request.method == 'POST':
        period = request.form.get('period')
        item_type = request.form.get('type').upper()
        amount = request.form.get('amount')

        if item_type.lower() not in ['a', 'b', 'c']:
            flash("Invalid item type", category='error')
        elif not amount.isdigit() or int(amount) <= 0:
            flash("Invalid amount", category='error')
        else:
            order_quantities = calculate_order_quantities(item_type, amount)
            if order_quantities is None:
                flash("Invalid item type", category='error')
            else:
                new_order = Order(item_type=item_type,
                                  blue=order_quantities['blue'],
                                  red=order_quantities['red'],
                                  grey=order_quantities['grey'],
                                  amount=int(amount))
            db.session.add(new_order)
            db.session.commit()

            newRecord = Record(OrderId=new_order.id, period=period, activity="Order created")
            db.session.add(newRecord)
            db.session.commit()
            flash("Bestelling geplaatst", category='success')

    # Query records for orders created today
    records = Record.query.filter(
        db.func.date(Record.date_time) == today, 
        Record.activity == "Order created"
    ).all()

    # Query records for orders finished today
    records_finished = Record.query.filter(
        db.func.date(Record.date_time) == today,
        Record.activity == "Order finished"
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

    order_dates_finished = {
        record.OrderId: record.period for record in records_finished
    }

    return render_template("customer.html", orders=orders, order_dates=order_dates, order_dates_finished=order_dates_finished, deliver_by= int(os.getenv('DELIVERY_DEADLINE')))

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

    # Query orders based on extracted order ids
    orders_created = Order.query.filter(Order.id.in_(order_ids_created)).all()
    
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
                           order_dates_finished=order_dates_finished,
                           deliver_by= int(os.getenv('DELIVERY_DEADLINE')))

@views.route('/voorraadbeheer', methods=['GET', 'POST'])
def inventorymanagement():
    client_timezone = pytz.timezone('Europe/Amsterdam')
    today = datetime.now(timezone.utc).date()
    if request.method == 'POST':
        action = request.form.get('action')
        order_id = request.form.get('order_id')
        period = request.form.get('period')
        blue = int(request.form.get('blue', 0))
        red = int(request.form.get('red', 0))
        grey = int(request.form.get('grey', 0))

        if action == 'create_supply_order':
            new_supply_order = SupplyOrder(blue=blue, red=red, grey=grey)
            db.session.add(new_supply_order)
            db.session.commit()

            newRecord = Record(SupplyOrderId=new_supply_order.id, period=period, activity="Supply order created")
            db.session.add(newRecord)
            db.session.commit()
            flash("Voorraad bestelling geplaatst", category='success')

        elif action == 'update_order_status':
            order = Order.query.get(order_id)
            if order is None:
                flash("Order not found", category='error')
            else:
                stock = Stock.query.first()

                if stock.blue < blue or stock.red < red or stock.grey < grey:
                    flash("Insufficient stock to fulfill the order", category='error')
                else:
                    stock.blue -= blue
                    stock.red -= red
                    stock.grey -= grey
                    create_record(order_id=order.id, period=period, activity="Inventory management finished")
                    db.session.commit()

                    flash("Order updated", category='success')

    # Get stock
    stock = Stock.query.first()

    # Subquery to get all order IDs with an "Inventory management finished" record
    finished_subquery = db.session.query(Record.OrderId).filter(
        db.func.date(Record.date_time) == today,
        Record.activity == "Inventory management finished"
    ).subquery()

    # Get all created orders today that do not have an "Inventory management finished" record
    created_records = Record.query.filter(
        db.func.date(Record.date_time) == today,
        Record.activity == "Order created",
        ~Record.OrderId.in_(finished_subquery)
    ).all()

    order_ids = [record.OrderId for record in created_records]
    orders = Order.query.filter(Order.id.in_(order_ids)).all()

    # Create a dictionary to map order ids to their "Order created" dates
    order_dates = {
        record.OrderId: (
            record.date_time.replace(tzinfo=pytz.utc).astimezone(client_timezone).strftime('%Y-%m-%d %H:%M'),
            record.period
        ) for record in created_records
    }

    # Get all created supply orders today
    supply_created_records = Record.query.filter(
        db.func.date(Record.date_time) == today,
        Record.activity == "Supply order created"
    ).all()

    supply_order_ids = [record.SupplyOrderId for record in supply_created_records]
    supply_orders = SupplyOrder.query.filter(SupplyOrder.id.in_(supply_order_ids)).all()

    return render_template(
        "inventorymanager.html", 
        orders=orders, 
        order_dates=order_dates, 
        stock=stock, 
        supply_orders=supply_orders
    )

@views.route('/leverancier', methods=['GET', 'POST'])
def supplier():
    today = datetime.now(timezone.utc).date()
    # Retrieve all supply orders created today
    supply_orders = SupplyOrder.query.join(Record).filter(
        db.func.date(Record.date_time) == today,
        Record.activity == "Supply order created"
    ).all()

    return render_template("supplier.html", supply_orders=supply_orders)

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
                create_record(order_id=order.id, activity="Customer approved order")
            else:
                create_record(order_id=order.id, activity="Customer disapproved order")
        elif type == 'accountmanager':
            order.accountmanager_checked = correct
            if correct:
                create_record(order_id=order.id, activity="Account manager approved order")
            else:
                create_record(order_id=order.id, activity="Account manager disapproved order")
        else:
            return jsonify({'error': 'Invalid type provided'}), 400

        if correct and type == 'accountmanager' and actual_delivery_period is not None:
            try:
                actual_delivery_period = int(actual_delivery_period)
                # Create a new record for "Order finished"
                create_record(order_id=order.id, period=actual_delivery_period, activity="Order finished")
            except ValueError:
                return jsonify({'error': 'Invalid actual delivery period provided'}), 400

        # Commit the changes
        db.session.commit()

        return jsonify({'message': 'Order status updated successfully'}), 200
    else:
        return jsonify({'error': 'Order not found'}), 404

@views.route('/update_supply_order_status', methods=['POST'])
def update_supply_order_status():
    data = request.get_json()
    supply_order_id = data.get('supply_order_id')
    correct = data.get('correct')

    if supply_order_id is None or correct is None:
        return jsonify({'error': 'Missing supply_order_id or correct parameter'}), 400

    supply_order = SupplyOrder.query.get(supply_order_id)
    if supply_order is None:
        return jsonify({'error': 'Supply order not found'}), 404

    supply_order.correct_delivery = correct

    if correct:
        stock = Stock.query.first()
        stock.blue += supply_order.blue
        stock.red += supply_order.red
        stock.grey += supply_order.grey
        create_record(supply_order_id=supply_order.id, activity="correct delivery")
    else:
        stock = Stock.query.first()
        stock.blue -= supply_order.blue
        stock.red -= supply_order.red
        stock.grey -= supply_order.grey
        create_record(supply_order_id=supply_order.id, activity="Incorrect delivery")
    db.session.commit()

    return jsonify({
        'message': 'Supply order status updated successfully',
        'current_stock': {
            'blue': stock.blue,
            'red': stock.red,
            'grey': stock.grey
        }
    })

@views.route('update_supply_order_fulfilled_status', methods=['POST'])
def update_supply_order_fulfilled_status():
    data = request.get_json()
    supply_order_id = data.get('supply_order_id')
    fulfilled = data.get('fulfilled')

    if supply_order_id is None or fulfilled is None:
        return jsonify({'error': 'Missing supply_order_id or fulfilled parameter'}), 400

    supply_order = SupplyOrder.query.get(supply_order_id)
    if supply_order is None:
        return jsonify({'error': 'Supply order not found'}), 404

    supply_order.fulfilled = fulfilled
    create_record(supply_order_id=supply_order.id, activity="Supply order fulfilled")
    db.session.commit()

    return jsonify({
        'message': 'Supply order fulfilled status updated successfully'
    })

@views.route('/reset_stock', methods=['POST'])
def reset_stock():
    stock = Stock.query.first()
    stock.blue = 0
    stock.red = 0
    stock.grey = 0
    db.session.commit()

    return jsonify({
        'message': 'Stock reset successfully',
        'current_stock': {
            'blue': stock.blue,
            'red': stock.red,
            'grey': stock.grey
        }
    })

def create_record(order_id=None, supply_order_id=None, period=-1, activity=None):
    if activity is None:
        raise ValueError("Activity parameter is required")

    if order_id is None and supply_order_id is None:
        raise ValueError("Either order_id or supply_order_id must be provided")

    if order_id is not None:
        new_record = Record(OrderId=order_id, period=period, activity=activity)
    elif supply_order_id is not None:
        new_record = Record(SupplyOrderId=supply_order_id, period=period, activity=activity)

    db.session.add(new_record)

def calculate_order_quantities(item_type, amount):
    if item_type not in order_specifications:
        return None  # Invalid item type

    specifications = order_specifications[item_type].copy()
    if amount == '2':
        for key in specifications:
            specifications[key] *= 2  # Double the quantities if amount is 2

    return specifications