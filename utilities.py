from functools import wraps
from json import dumps

from flask import Response
from flask_jwt_extended import get_jwt

ADMIN_ROLE_ID = 1
ADMIN_ROLE_NAME = 'admin'

CUSTOMER_ROLE_ID = 2
CUSTOMER_ROLE_NAME = 'customer'

WAREHOUSE_WORKER_ROLE_ID = 3
WAREHOUSE_WORKER_ROLE_NAME = 'warehouse_worker'

ORDER_PENDING_STATUS = 'PENDING'
ORDER_COMPLETE_STATUS = 'COMPLETE'


def create_error_response(error_message, status):
    return Response(dumps({'message': error_message}), status=status, mimetype='application/json')


def role_required(role_name):

    def inner_role_required(function):

        @wraps(function)
        def decorator(*args, **kwargs):
            token_claims = get_jwt()
            if role_name in token_claims['roles']:
                return function(*args, **kwargs)
            else:
                return Response(dumps({'msg': 'Missing Authorization Header'}), status=401, mimetype='application/json')

        return decorator

    return inner_role_required


def is_positive_integer(string_representation):
    try:
        integer = int(string_representation)
        return True if integer > 0 else False
    except ValueError:
        return False
