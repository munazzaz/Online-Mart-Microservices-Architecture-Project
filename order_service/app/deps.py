from aiokafka import AIOKafkaProducer
from sqlmodel import Session
from app.db_engine import get_session as get_db_session
from app.settings import BOOTSTRAP_SERVER
import httpx

def get_session() -> Session:
    return next(get_db_session())

async def get_kafka_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()



async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client