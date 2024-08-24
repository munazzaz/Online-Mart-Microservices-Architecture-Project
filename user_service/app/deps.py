from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
import asyncio
import json

from app.service import create_user, authenticate as delete_user, update_user
from app.database import get_db

from app.settings import BOOTSTRAP_SERVER, KAFKA_CONSUMER_GROUP_ID_FOR_USER, KAFKA_USER_TOPIC

# Kafka Producer Dependency
async def get_kafka_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVER
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

# Kafka Consumer Dependency
async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=KAFKA_CONSUMER_GROUP_ID_FOR_USER
    )
    await consumer.start()
    try:
        async for message in consumer:
            user_data = json.loads(message.value.decode())
            with next(get_db()) as db:
                if user_data['action'] == 'create':
                    create_user(db, user_data['user'])
                elif user_data['action'] == 'update':
                    update_user(db, user_data['user'])
                elif user_data['action'] == 'delete':
                    delete_user(db, user_data['user_id'])
    finally:
        await consumer.stop()

# Context manager to handle app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(consume_messages(KAFKA_USER_TOPIC, BOOTSTRAP_SERVER))
    try:
        yield
    finally:
        consumer_task.cancel()
        await consumer_task
