from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from sqlalchemy import func

from applications.configuration import Configuration
from applications.models import database, Product, OrderProduct, Category, ProductCategory
from utilities import role_required, ADMIN_ROLE_NAME

application = Flask(__name__)
application.config.from_object(Configuration)

jwt_manager = JWTManager(application)


@application.route('/productStatistics', methods=['GET'])
@jwt_required()
@role_required(role_name=ADMIN_ROLE_NAME)
def get_product_statistics():
    results = Product.query.join(OrderProduct)\
        .group_by(Product.id)\
        .with_entities(Product.name, func.sum(OrderProduct.requested_quantity),
                       func.sum(OrderProduct.received_quantity))\
        .all()

    json_response = {
        'statistics': [
            {
                'name': product_name,
                'sold': int(sum_requested),
                'waiting': int(sum_requested - sum_received)
            }
            for product_name, sum_requested, sum_received in sorted(results, key=lambda obj: obj[0])
        ]
    }

    return jsonify(json_response)


@application.route('/categoryStatistics', methods=['GET'])
@jwt_required()
@role_required(role_name=ADMIN_ROLE_NAME)
def get_category_statistics():
    ordered_categories = Category.query.outerjoin(ProductCategory).outerjoin(Product).outerjoin(OrderProduct)\
        .group_by(Category.id)\
        .order_by(func.sum(OrderProduct.requested_quantity).desc(), Category.name)\
        .all()

    return jsonify({'statistics': [category.name for category in ordered_categories]})


if __name__ == '__main__':
    database.init_app(application)
    application.run(host='0.0.0.0', debug=True)
