from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str)
KAFKA_ORDER_CREATED_TOPIC = config("KAFKA_ORDER_CREATED_TOPIC", cast=str)
KAFKA_ORDER_DELETED_TOPIC = config("KAFKA_ORDER_DELETED_TOPIC", cast=str)
KAFKA_ORDER_UPDATED_TOPIC = config("KAFKA_ORDER_UPDATED_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_ORDER = config("KAFKA_CONSUMER_GROUP_ID_FOR_ORDER", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION = config("KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION", cast=str)



SMTP_SERVER = config("SMTP_SERVER", cast=str)
SMTP_PORT = config("SMTP_PORT", cast=int)
SMTP_USERNAME = config("SMTP_USERNAME", cast=str)
SMTP_PASSWORD = config("SMTP_PASSWORD", cast=str)
FROM_EMAIL = config("FROM_EMAIL", cast=str)





