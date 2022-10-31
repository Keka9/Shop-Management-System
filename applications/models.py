from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = 'product_category'

    id_product = database.Column(database.Integer, database.ForeignKey('products.id'), primary_key=True)
    id_category = database.Column(database.Integer, database.ForeignKey('categories.id'), primary_key=True)


class OrderProduct(database.Model):
    __tablename__ = 'order_product'

    id_order = database.Column(database.Integer, database.ForeignKey('orders.id'), primary_key=True)
    id_product = database.Column(database.Integer, database.ForeignKey('products.id'), primary_key=True)
    requested_quantity = database.Column(database.Integer, nullable=False)
    received_quantity = database.Column(database.Integer, nullable=False)
    product_price = database.Column(database.Float, nullable=False)


class Order(database.Model):
    __tablename__ = 'orders'

    id = database.Column(database.Integer, primary_key=True)
    total_price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False)
    created_at = database.Column(database.DateTime, nullable=False)
    customer_email = database.Column(database.String(256), nullable=False)

    products = database.relationship('Product', secondary=OrderProduct.__table__, back_populates='orders')


class Product(database.Model):
    __tablename__ = 'products'

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)
    price = database.Column(database.Float, nullable=False)
    available_quantity = database.Column(database.Integer, nullable=False)

    orders = database.relationship('Order', secondary=OrderProduct.__table__, back_populates='products')
    categories = database.relationship('Category', secondary=ProductCategory.__table__, back_populates='products')


class Category(database.Model):
    __tablename__ = 'categories'

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)

    products = database.relationship('Product', secondary=ProductCategory.__table__, back_populates='categories')
