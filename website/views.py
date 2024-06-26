from flask import Blueprint, render_template, request, flash

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/klant', methods=['GET', 'POST'])
def customer():
    if request.method == 'POST':
        period = request.form.get('period')
        itemType = request.form.get('type')
        amount = request.form.get('amount')

        # Correctly check if itemType is 'a', 'b', or 'c'
        if itemType.lower() not in ['a', 'b', 'c']:
            flash("Invalid item type", category='error')
        else:
            flash("Order added", category='success')

    return render_template("customer.html")

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