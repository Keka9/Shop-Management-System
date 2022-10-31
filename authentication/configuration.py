from datetime import timedelta


class Configuration:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@authentication_database_server:3306/authentication'

    JWT_SECRET_KEY = '+MbQeThWmZq4t7w!z%C*FaJ@NcRfUjXn'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
