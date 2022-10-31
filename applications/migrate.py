from flask import Flask
from flask_migrate import Migrate, init, upgrade, migrate
from sqlalchemy_utils import database_exists, create_database

from applications.configuration import Configuration
from applications.models import database

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
                done = True
        except Exception:
            pass
