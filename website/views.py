from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/klant')
def customer():
    return render_template("customer.html")

@views.route('/accountmanager')
def accountmanager():
    return render_template("accountmanager.html")

@views.route('/voorraadbeheer')
def inventorykmanagement():
    return render_template("inventorymanager.html")

@views.route('/leverancier')
def supplier():
    return render_template("supplier.html")

@views.route('/productie')
def production():
    return render_template("production.html")