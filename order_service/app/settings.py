from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

# Convert DATABASE_URL from Secret to string
DATABASE_URL = config("DATABASE_URL", cast=Secret).__str__()
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str)
KAFKA_ORDER_CREATED_TOPIC = config("KAFKA_ORDER_CREATED_TOPIC", cast=str)
KAFKA_ORDER_DELETED_TOPIC = config("KAFKA_ORDER_DELETED_TOPIC", cast=str)
KAFKA_ORDER_UPDATED_TOPIC = config("KAFKA_ORDER_UPDATED_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_ORDER = config("KAFKA_CONSUMER_GROUP_ID_FOR_ORDER", cast=str)
