import csv
import io
from json import dumps

from flask import Flask, Response, request
from flask_jwt_extended import jwt_required, JWTManager
from redis.client import Redis

from applications.configuration import Configuration
from utilities import create_error_response, role_required, WAREHOUSE_WORKER_ROLE_NAME, is_positive_integer

application = Flask(__name__)
application.config.from_object(Configuration)

jwt_manager = JWTManager(application)


@application.route('/update', methods=['POST'])
@jwt_required()
@role_required(role_name=WAREHOUSE_WORKER_ROLE_NAME)
def send_delivery_information():
    file_missing_message = 'Field file is missing.'
    incorrect_number_of_values_message_format = 'Incorrect number of values on line {}.'
    incorrect_quantity_message_format = 'Incorrect quantity on line {}.'
    incorrect_price_message_format = 'Incorrect price on line {}.'

    file = request.files.get('file', '')
    if file == '':
        return create_error_response(file_missing_message, 400)

    content = file.stream.read().decode('utf-8')
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    number_of_values_in_row = 4
    delivered_products = list()

    for index, row in enumerate(reader):
        if len(row) != number_of_values_in_row:
            return create_error_response(incorrect_number_of_values_message_format.format(index), 400)

        if not is_positive_integer(row[2]):
            return create_error_response(incorrect_quantity_message_format.format(index), 400)

        try:
            if float(row[3]) <= 0:
                return create_error_response(incorrect_price_message_format.format(index), 400)
        except ValueError:
            return create_error_response(incorrect_price_message_format.format(index), 400)

        delivered_products.append({
            'name': row[1].strip(),
            'delivery_price': float(row[3]),
            'delivery_quantity': int(row[2]),
            'categories': [category.strip() for category in row[0].split('|')]
        })

    with Redis(host=Configuration.REDIS_HOST) as redis_client:
        redis_client.publish(Configuration.REDIS_CHANNEL_NAME, dumps(delivered_products))

    return Response(status=200, mimetype='application/json')


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
