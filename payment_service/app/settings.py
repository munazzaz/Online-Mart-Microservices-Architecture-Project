from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

# Convert DATABASE_URL and STRIPE_SECRET_KEY from Secret to string
DATABASE_URL = config("DATABASE_URL", cast=Secret).__str__()
STRIPE_SECRET_KEY = config("STRIPE_API_KEY", cast=Secret).__str__()
KAFKA_BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_PAYMENT_TOPIC = config("KAFKA_PAYMENT_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT", cast=str)
BASE_URL = config("BASE_URL", cast=str)



