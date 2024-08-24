from starlette.config import Config
from starlette.datastructures import Secret
from typing import Optional

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

# config = Config(".env")

DATABASE_URL = config("DATABASE_URL", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)
ALGORITHM = config("ALGORITHM", cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
KAFKA_INVENTORY_TOPIC = config("KAFKA_INVENTORY_TOPIC", cast=str)
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str)
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_USER = config("KAFKA_CONSUMER_GROUP_ID_FOR_USER", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)
