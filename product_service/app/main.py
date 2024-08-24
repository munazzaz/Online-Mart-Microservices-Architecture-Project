# Import necessary modules
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated, AsyncGenerator
from sqlmodel import Session, SQLModel
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.product_model import Product, ProductUpdate
from app.crud.product_crud import add_new_product, get_all_products, get_product_by_id, delete_product_by_id, update_product_by_id
from app.deps import get_session, get_kafka_producer

# Create the database and tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

# Function to consume messages from Kafka
async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT
    )

    await consumer.start()
    try:
        async for message in consumer:
            product_data = json.loads(message.value.decode())
            with next(get_session()) as session:
                if product_data['action'] == 'create':
                    add_new_product(product_data=Product(**product_data['product']), session=session)
                elif product_data['action'] == 'update':
                    update_product_by_id(product_id=product_data['product']['id'], to_update_product_data=ProductUpdate(**product_data['product']), session=session)
                elif product_data['action'] == 'delete':
                    delete_product_by_id(product_id=product_data['product']['id'], session=session)
    finally:
        await consumer.stop()

# Context manager to handle app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    consumer_task = asyncio.create_task(consume_messages(settings.KAFKA_PRODUCT_TOPIC, settings.BOOTSTRAP_SERVER))
    try:
        yield
    finally:
        consumer_task.cancel()
        await consumer_task

# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Product Service API",
    version="0.0.1",
    description = "The Product Service API is a comprehensive solution for managing product data within your application. It provides endpoints for creating, updating, retrieving, and deleting product information, ensuring that your product catalog is always up-to-date. ",
    servers=[
        {
            "url": "http://127.0.0.1:8005/",
            "description": "Local Development Server"
        }
        ]
)

@app.get("/")
def read_root():
    return {"Hello": "Product Service"}


@app.post("/manage-products/", response_model=Product)
async def create_new_product(product: Product, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    product_dict = product.dict()
    product_json = json.dumps({'action': 'create', 'product': product_dict}).encode("utf-8")
    key = str(product.id).encode('utf-8')  # Unique key for each product
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json, key=key)
    new_product = add_new_product(product, session)
    return new_product

@app.patch("/manage-products/{product_id}", response_model=Product)
async def update_single_product(product_id: int, product: ProductUpdate, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    updated_product = update_product_by_id(product_id=product_id, to_update_product_data=product, session=session)
    product_dict = product.dict(exclude_unset=True)
    product_dict['id'] = product_id
    product_json = json.dumps({'action': 'update', 'product': product_dict}).encode("utf-8")
    key = str(product_id).encode('utf-8')  # Unique key for each product
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json, key=key)
    return updated_product

@app.delete("/manage-products/{product_id}", response_model=dict)
async def delete_single_product(product_id: int, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    delete_product_by_id(product_id=product_id, session=session)
    product_json = json.dumps({'action': 'delete', 'product': {'id': product_id}}).encode("utf-8")
    key = str(product_id).encode('utf-8')  # Unique key for each product
    await producer.send_and_wait(settings.KAFKA_PRODUCT_TOPIC, product_json, key=key)
    return {"message": "Product Deleted Successfully"}


@app.get("/manage-products/all", response_model=list[Product])
def call_all_products(session: Annotated[Session, Depends(get_session)]):
    return get_all_products(session)

@app.get("/manage-products/{product_id}", response_model=Product)
def get_single_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    return get_product_by_id(product_id=product_id, session=session)



