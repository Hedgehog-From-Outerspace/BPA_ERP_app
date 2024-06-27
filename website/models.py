from . import db

class Order(db.Model):
    __tablename__ = 'Order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_type = db.Column(db.String(1), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    blue = db.Column(db.Integer, nullable=True)
    red = db.Column(db.Integer, nullable=True)
    grey = db.Column(db.Integer, nullable=True)
    accountmanager_checked = db.Column(db.Boolean, nullable=True)
    customer_checked = db.Column(db.Boolean, nullable=True)
    records = db.relationship('Record', backref='Order', lazy=True)

class SupplyOrder(db.Model):
    __tablename__ = 'SupplyOrder'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blue = db.Column(db.Integer, nullable=False)
    red = db.Column(db.Integer, nullable=False)
    grey = db.Column(db.Integer, nullable=False)
    incorrect_delivery = db.Column(db.Boolean, nullable=True)
    records = db.relationship('Record', backref='SupplyOrder', lazy=True)

class Record(db.Model):
    __tablename__ = 'Record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderId = db.Column(db.Integer, db.ForeignKey('Order.id'), nullable=True)
    SupplyOrderId = db.Column(db.Integer, db.ForeignKey('SupplyOrder.id'), nullable=True)
    date_time = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    period = db.Column(db.Integer, nullable=False)
    activity = db.Column(db.String(100), nullable=False)

class Stock(db.Model):
    __tablename__ = 'Stock'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blue = db.Column(db.Integer, nullable=False)
    red = db.Column(db.Integer, nullable=False)
    grey = db.Column(db.Integer, nullable=False)
