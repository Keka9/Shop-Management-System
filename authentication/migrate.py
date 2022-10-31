from flask import Flask
from flask_migrate import Migrate, init, upgrade, migrate
from sqlalchemy_utils import database_exists, create_database

from authentication.configuration import Configuration
from authentication.models import database, Role, User, UserRole
from utilities import ADMIN_ROLE_ID, ADMIN_ROLE_NAME, CUSTOMER_ROLE_ID, CUSTOMER_ROLE_NAME, WAREHOUSE_WORKER_ROLE_ID, \
    WAREHOUSE_WORKER_ROLE_NAME

application = Flask(__name__)
application.config.from_object(Configuration)

migrate_object = Migrate(application, database)


if __name__ == '__main__':
    done = False

    while not done:
        try:
            if not database_exists(Configuration.SQLALCHEMY_DATABASE_URI):
                create_database(Configuration.SQLALCHEMY_DATABASE_URI)

            database.init_app(application)

            with application.app_context():
                init()
                migrate(message='Production migration.')
                upgrade()

                database.session.add(Role(id=ADMIN_ROLE_ID, name=ADMIN_ROLE_NAME))
                database.session.add(Role(id=CUSTOMER_ROLE_ID, name=CUSTOMER_ROLE_NAME))
                database.session.add(Role(id=WAREHOUSE_WORKER_ROLE_ID, name=WAREHOUSE_WORKER_ROLE_NAME))

                admin = User(forename='admin', surname='admin', email='admin@admin.com', password='1')
                database.session.add(admin)
                database.session.commit()

                database.session.add(UserRole(id_user=admin.id, id_role=ADMIN_ROLE_ID))
                database.session.commit()

                done = True
        except Exception:
            pass
