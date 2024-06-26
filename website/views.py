from flask import Blueprint, render_template, request, flash
from .models import Order, SupplyOrder, Record
from . import db
from datetime import datetime, timezone

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/klant', methods=['GET', 'POST'])
def customer():
    if request.method == 'POST':
        period = request.form.get('period')
        item_type = request.form.get('type')
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


    for order in orders:
        print(order.id, order.item_type, order.amount)

    for record in records:
        print(record.OrderId, record.period, record.activity, record.date_time)

    return render_template("customer.html", orders=orders, records=records)

@views.route('/accountmanager', methods=['GET', 'POST'])
def accountmanager():
    return render_template("accountmanager.html")

@views.route('/voorraadbeheer', methods=['GET', 'POST'])
def inventorykmanagement():
    return render_template("inventorymanager.html")

@views.route('/leverancier', methods=['GET', 'POST'])
def supplier():
    return render_template("supplier.html")

@views.route('/productie', methods=['GET', 'POST'])
def production():
    return render_template("production.html")