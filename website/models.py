from . import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_type = db.Column(db.String(1), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    blue = db.Column(db.Integer, nullable=True)
    red = db.Column(db.Integer, nullable=True)
    grey = db.Column(db.Integer, nullable=True)
    accountmanager_checked = db.Column(db.Boolean, nullable=True)
    records = db.relationship('Record', backref='order', lazy=True)

class SupplyOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blue = db.Column(db.Integer, nullable=False)
    red = db.Column(db.Integer, nullable=False)
    grey = db.Column(db.Integer, nullable=False)
    incorrect_delivery = db.Column(db.Boolean, nullable=True)
    records = db.relationship('Record', backref='supplyorder', lazy=True)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderId = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    SupplyOrderId = db.Column(db.Integer, db.ForeignKey('supplyorder.id'), nullable=True)
    date_time = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    period = db.Column(db.Integer, nullable=False)
    activity = db.Column(db.String(100), nullable=False)

