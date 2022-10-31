
class Configuration:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@shop_database_server:3306/shop'

    JWT_SECRET_KEY = '+MbQeThWmZq4t7w!z%C*FaJ@NcRfUjXn'

    REDIS_HOST = 'redis'
    REDIS_CHANNEL_NAME = 'delivered_products'
