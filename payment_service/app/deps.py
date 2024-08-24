from sqlmodel import Session
from app.db_engine import engine
from aiokafka import AIOKafkaProducer
from app import settings
from typing import AsyncIterator

def get_session() -> AsyncIterator[Session]:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

async def get_kafka_producer() -> AsyncIterator[AIOKafkaProducer]:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
