from datetime import datetime, timezone
from json import dumps

from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from applications.configuration import Configuration
from applications.models import database, Product, ProductCategory, Category, Order, OrderProduct
from utilities import role_required, CUSTOMER_ROLE_NAME, create_error_response, ORDER_COMPLETE_STATUS, \
    ORDER_PENDING_STATUS

application = Flask(__name__)
application.config.from_object(Configuration)

jwt_manager = JWTManager(application)


@application.route('/search', methods=['GET'])
@jwt_required()
@role_required(role_name=CUSTOMER_ROLE_NAME)
def search_products():
    product_name = request.args.get('name', '')
    category_name = request.args.get('category', '')

    results = Product.query.join(ProductCategory).join(Category).add_entity(Category)\
        .filter(Product.name.like(f'%{product_name}%'), Category.name.like(f'%{category_name}%'))\
        .all()

    products = set()
    categories = set()

    for result in results:
        if result[0] not in products:
            products.add(result[0])
        if result[1] not in categories:
            categories.add(result[1])

    json_response = {
        'categories': sorted([category.name for category in categories]),
        'products': [
            {
                'categories': sorted([category.name for category in product.categories]),
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': product.available_quantity
            }
            for product in sorted(products, key=lambda obj: obj.id)
        ]
    }

    return jsonify(json_response)


@application.route('/order', methods=['POST'])
@jwt_required()
@role_required(role_name=CUSTOMER_ROLE_NAME)
def make_an_order():
    requests_missing_message = 'Field requests is missing.'
    id_missing_message_format = 'Product id is missing for request number {}.'
    quantity_missing_message_format = 'Product quantity is missing for request number {}.'
    invalid_id_message_format = 'Invalid product id for request number {}.'
    invalid_quantity_message_format = 'Invalid product quantity for request number {}.'
    invalid_product_message_format = 'Invalid product for request number {}.'

    order_requests = request.json.get('requests', '')
    if order_requests == '':
        return create_error_response(requests_missing_message, 400)

    parsed_information = list()

    for index, order_request in enumerate(order_requests):
        product_id = order_request.get('id', '')
        if product_id == '':
            return create_error_response(id_missing_message_format.format(index), 400)

        wanted_quantity = order_request.get('quantity', '')
        if wanted_quantity == '':
            return create_error_response(quantity_missing_message_format.format(index), 400)

        if not isinstance(product_id, int) or product_id <= 0:
            return create_error_response(invalid_id_message_format.format(index), 400)

        if not isinstance(wanted_quantity, int) or wanted_quantity <= 0:
            return create_error_response(invalid_quantity_message_format.format(index), 400)

        product_in_database = Product.query.filter(Product.id == product_id).first()
        if product_in_database is None:
            return create_error_response(invalid_product_message_format.format(index), 400)

        parsed_information.append((product_in_database, wanted_quantity))

    customer_email = get_jwt_identity()
    new_order = Order(total_price=0.0, status='', created_at=datetime.now(timezone.utc), customer_email=customer_email)
    database.session.add(new_order)
    database.session.commit()

    order_complete = True

    for product_in_database, wanted_quantity in parsed_information:
        received_quantity = wanted_quantity if product_in_database.available_quantity >= wanted_quantity \
            else product_in_database.available_quantity

        if product_in_database.available_quantity < wanted_quantity:
            order_complete = False

        product_in_database.available_quantity -= received_quantity
        new_order.total_price += wanted_quantity * product_in_database.price

        order_product = OrderProduct(id_order=new_order.id, id_product=product_in_database.id,
                                     requested_quantity=wanted_quantity, received_quantity=received_quantity,
                                     product_price=product_in_database.price)
        database.session.add(order_product)

    new_order.status = ORDER_COMPLETE_STATUS if order_complete else ORDER_PENDING_STATUS
    database.session.commit()

    return Response(dumps({'id': new_order.id}), status=200, mimetype='application/json')


@application.route('/status', methods=['GET'])
@jwt_required()
@role_required(role_name=CUSTOMER_ROLE_NAME)
def get_orders_for_customer():
    customer_orders = Order.query.filter(Order.customer_email == get_jwt_identity()).all()

    json_response = {
        'orders': [
            {
                'products': [
                    {
                        'categories': sorted([category.name for category in product.categories]),
                        'name': product.name,
                        'price': order_product.product_price,
                        'received': order_product.received_quantity,
                        'requested': order_product.requested_quantity
                    }
                    for product, order_product in sorted(Product.query.join(OrderProduct).add_entity(OrderProduct)
                                                         .filter(OrderProduct.id_order == order.id).all(),
                                                         key=lambda obj: obj[0].id)
                ],
                'price': order.total_price,
                'status': order.status,
                'timestamp': order.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            for order in sorted(customer_orders, key=lambda obj: obj.id)
        ]
    }

    return jsonify(json_response)


if __name__ == '__main__':
    database.init_app(application)
    application.run(host='0.0.0.0', debug=True)
