from json import loads

from flask import Flask
from redis.client import Redis

from applications.configuration import Configuration
from applications.models import database, Product, Category, ProductCategory, OrderProduct, Order
from utilities import ORDER_COMPLETE_STATUS

application = Flask(__name__)
application.config.from_object(Configuration)


def check_product_and_update_shop(product):
    product_in_database = Product.query.filter(Product.name == product['name']).first()

    if product_in_database is None:
        add_new_product(product)
    else:
        if set(product['categories']) != set([category.name for category in product_in_database.categories]):
            return
        update_product_information(product, product_in_database)
        update_pending_orders(product_in_database)


def add_new_product(product):
    new_product = Product(name=product['name'], price=product['delivery_price'],
                          available_quantity=product['delivery_quantity'])
    database.session.add(new_product)
    database.session.commit()

    categories_in_database = [category for category in Category.query.all()]
    for category_name in product['categories']:
        category_in_database = next((category for category in categories_in_database if category.name == category_name),
                                    None)

        if category_in_database is not None:
            database.session.add(ProductCategory(id_product=new_product.id, id_category=category_in_database.id))
            database.session.commit()
        else:
            new_category = Category(name=category_name)
            database.session.add(new_category)
            database.session.commit()

            categories_in_database.append(new_category)

            database.session.add(ProductCategory(id_product=new_product.id, id_category=new_category.id))
            database.session.commit()


def update_product_information(product, product_in_database):
    new_price = (product_in_database.available_quantity * product_in_database.price + product['delivery_quantity']
                 * product['delivery_price']) / (product_in_database.available_quantity + product['delivery_quantity'])
    product_in_database.price = new_price
    product_in_database.available_quantity += product['delivery_quantity']
    database.session.commit()


def update_pending_orders(product_in_database):
    results = Product.query.join(OrderProduct).join(Order).add_entity(OrderProduct).add_entity(Order)\
        .filter(OrderProduct.received_quantity < OrderProduct.requested_quantity, Product.id == product_in_database.id)\
        .order_by(Order.created_at)\
        .all()

    for result in results:
        needed_quantity = result[1].requested_quantity - result[1].received_quantity

        if product_in_database.available_quantity >= needed_quantity:
            product_in_database.available_quantity -= needed_quantity
            result[1].received_quantity += needed_quantity
            database.session.commit()

            try_to_complete_order(result[2])

            if product_in_database.available_quantity == 0:
                break
        else:
            available_quantity = product_in_database.available_quantity
            product_in_database.available_quantity = 0
            result[1].received_quantity += available_quantity
            database.session.commit()
            break


def try_to_complete_order(order):
    order_products = OrderProduct.query.filter(OrderProduct.id_order == order.id).all()
    order_complete = True

    for order_product in order_products:
        if order_product.requested_quantity > order_product.received_quantity:
            order_complete = False
            break

    if order_complete:
        order.status = ORDER_COMPLETE_STATUS
        database.session.commit()


if __name__ == '__main__':
    database.init_app(application)

    server_up = False
    while not server_up:
        try:
            with Redis(host=Configuration.REDIS_HOST) as redis_client:
                redis_client.ping()
                server_up = True
        except Exception:
            pass

    with Redis(host=Configuration.REDIS_HOST) as redis_client:
        pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(Configuration.REDIS_CHANNEL_NAME)

        for message in pubsub.listen():
            delivered_products = loads(message['data'].decode('utf-8'))

            with application.app_context():
                for delivered_product in delivered_products:
                    check_product_and_update_shop(delivered_product)
