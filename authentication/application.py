import re

from flask import Flask, request, Response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    get_jwt

from configuration import Configuration
from models import database, User, UserRole
from utilities import create_error_response, CUSTOMER_ROLE_ID, WAREHOUSE_WORKER_ROLE_ID, ADMIN_ROLE_NAME, role_required

application = Flask(__name__)
application.config.from_object(Configuration)

jwt_manager = JWTManager(application)


@application.route('/register', methods=['POST'])
def register_new_user():
    field_missing_message_format = 'Field {} is missing.'
    invalid_email_message = 'Invalid email.'
    invalid_password_message = 'Invalid password.'
    email_exists_message = 'Email already exists.'

    forename = request.json.get('forename', '')
    if forename == '':
        return create_error_response(field_missing_message_format.format('forename'), 400)

    surname = request.json.get('surname', '')
    if surname == '':
        return create_error_response(field_missing_message_format.format('surname'), 400)

    email = request.json.get('email', '')
    if email == '':
        return create_error_response(field_missing_message_format.format('email'), 400)

    password = request.json.get('password', '')
    if password == '':
        return create_error_response(field_missing_message_format.format('password'), 400)

    is_customer = request.json.get('isCustomer', '')
    if is_customer == '':
        return create_error_response(field_missing_message_format.format('isCustomer'), 400)

    if not re.match(r'^[a-zA-Z0-9._-]+@([a-zA-Z0-9]{2,}\.)+[a-zA-Z0-9]{2,}$', email):
        return create_error_response(invalid_email_message, 400)

    matched_digits = re.search(r'\d', password)
    matched_lowercase_letters = re.search(r'[a-z]', password)
    matched_uppercase_letters = re.search(r'[A-Z]', password)
    min_password_length = 8

    if not matched_digits or not matched_lowercase_letters or not matched_uppercase_letters or \
            len(password) < min_password_length:
        return create_error_response(invalid_password_message, 400)

    if len(User.query.filter(User.email == email).all()) != 0:
        return create_error_response(email_exists_message, 400)

    user = User(forename=forename, surname=surname, email=email, password=password)
    database.session.add(user)
    database.session.commit()

    if is_customer:
        database.session.add(UserRole(id_user=user.id, id_role=CUSTOMER_ROLE_ID))
    else:
        database.session.add(UserRole(id_user=user.id, id_role=WAREHOUSE_WORKER_ROLE_ID))
    database.session.commit()

    return Response(status=200, mimetype='application/json')


@application.route('/login', methods=['POST'])
def login():
    field_missing_message_format = 'Field {} is missing.'
    invalid_email_message = 'Invalid email.'
    invalid_credentials_message = 'Invalid credentials.'

    email = request.json.get('email', '')
    if email == '':
        return create_error_response(field_missing_message_format.format('email'), 400)

    password = request.json.get('password', '')
    if password == '':
        return create_error_response(field_missing_message_format.format('password'), 400)

    if not re.match(r'^[a-zA-Z0-9._-]+@([a-zA-Z0-9]{2,}\.)+[a-zA-Z0-9]{2,}$', email):
        return create_error_response(invalid_email_message, 400)

    user = User.query.filter(User.email == email, User.password == password).first()
    if user is None:
        return create_error_response(invalid_credentials_message, 400)

    additional_claims = {
        'forename': user.forename,
        'surname': user.surname,
        'roles': [role.name for role in user.roles]
    }

    json_response = {
        'accessToken': create_access_token(identity=user.email, additional_claims=additional_claims),
        'refreshToken': create_refresh_token(identity=user.email, additional_claims=additional_claims)
    }

    return jsonify(json_response)


@application.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()

    additional_claims = {
        'forename': refresh_claims['forename'],
        'surname': refresh_claims['surname'],
        'roles': refresh_claims['roles']
    }

    return jsonify({'accessToken': create_access_token(identity=identity, additional_claims=additional_claims)})


@application.route('/delete', methods=['POST'])
@jwt_required()
@role_required(role_name=ADMIN_ROLE_NAME)
def delete_user():
    email_missing_message = 'Field email is missing.'
    invalid_email_message = 'Invalid email.'
    unknown_user_message = 'Unknown user.'

    email = request.json.get('email', '')
    if email == '':
        return create_error_response(email_missing_message, 400)

    if not re.match(r'^[a-zA-Z0-9._-]+@([a-zA-Z0-9]{2,}\.)+[a-zA-Z0-9]{2,}$', email):
        return create_error_response(invalid_email_message, 400)

    user = User.query.filter(User.email == email).first()
    if user is None:
        return create_error_response(unknown_user_message, 400)

    for user_role in UserRole.query.filter(UserRole.id_user == user.id).all():
        database.session.delete(user_role)
    database.session.commit()

    database.session.delete(user)
    database.session.commit()

    return Response(status=200, mimetype='application/json')


if __name__ == '__main__':
    database.init_app(application)
    application.run(host='0.0.0.0', debug=True)
