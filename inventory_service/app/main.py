from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated, AsyncGenerator
from sqlmodel import Session, SQLModel
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.inventory_model import Inventory, InventoryCreate, InventoryUpdate
from app.crud.inventory_crud import add_new_inventory, get_all_inventory, get_inventory_by_id, update_inventory_by_id, delete_inventory_by_id, validate_product_id, get_inventory_by_product_id
from app.deps import get_session, get_kafka_producer

# Create the database and tables
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

# Function to consume messages from Kafka
async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY
    )

    await consumer.start()
    try:
        async for message in consumer:
            event = json.loads(message.value.decode())
            with next(get_session()) as session:
                if event['action'] == 'create':
                    product_data = event['product']
                    inventory_data = InventoryCreate(
                        product_id=product_data['id'],
                        quantity=0,
                        stock_status='initial'
                    )
                    add_new_inventory(inventory_data, session)
                elif event['action'] == 'update':
                    update_inventory_by_id(inventory_id=event['inventory']['id'], to_update_inventory_data=InventoryUpdate(**event['inventory']), session=session)
                elif event['action'] == 'delete':
                    delete_inventory_by_id(inventory_id=event['inventory']['id'], session=session)
    finally:
        await consumer.stop()

# Context manager to handle app lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    consumer_task = asyncio.create_task(consume_messages(settings.KAFKA_INVENTORY_TOPIC, settings.BOOTSTRAP_SERVER))
    try:
        yield
    finally:
        consumer_task.cancel()
        await consumer_task

# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Inventory Service API",
    version="0.0.1",
    description = "The Inventory Service API is a crucial component for managing stock levels and ensuring product availability across your platform.",
    servers=[
        {
            "url": "http://127.0.0.1:8007/",
            "description": "Local Development Server"
        }
        ]
)

@app.get("/")
def read_root():
    return {"Hello": "Inventory Service"}

@app.post("/manage-inventory/", response_model=Inventory)
async def create_new_inventory(inventory: InventoryCreate, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    # Validate product_id
    validate_product_id(inventory.product_id)

    inventory_dict = inventory.dict()
    inventory_json = json.dumps({'action': 'create', 'inventory': inventory_dict}).encode("utf-8")
    key = str(inventory.product_id).encode('utf-8')  # Unique key for each product
    await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, inventory_json, key=key)
    new_inventory = add_new_inventory(inventory, session)
    return new_inventory

@app.patch("/manage-inventory/{inventory_id}", response_model=Inventory)
async def update_single_inventory(inventory_id: int, inventory: InventoryUpdate, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    updated_inventory = update_inventory_by_id(inventory_id=inventory_id, to_update_inventory_data=inventory, session=session)
    inventory_dict = inventory.dict(exclude_unset=True)
    inventory_dict['id'] = inventory_id
    inventory_json = json.dumps({'action': 'update', 'inventory': inventory_dict}).encode("utf-8")
    key = str(inventory_id).encode('utf-8')  # Unique key for each product
    await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, inventory_json, key=key)
    return updated_inventory

@app.delete("/manage-inventory/{inventory_id}", response_model=dict)
async def delete_single_inventory(inventory_id: int, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    delete_inventory_by_id(inventory_id=inventory_id, session=session)
    inventory_json = json.dumps({'action': 'delete', 'inventory': {'id': inventory_id}}).encode("utf-8")
    key = str(inventory_id).encode('utf-8')  # Unique key for each product
    await producer.send_and_wait(settings.KAFKA_INVENTORY_TOPIC, inventory_json, key=key)
    return {"message": "Inventory Deleted Successfully"}

@app.get("/manage-inventory/product/{product_id}", response_model=Inventory)
def get_inventory_by_product(product_id: int, session: Annotated[Session, Depends(get_session)]):
    inventory = get_inventory_by_product_id(product_id=product_id, session=session)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found for the provided product ID"
        )
    return inventory

@app.get("/manage-inventory/all", response_model=list[Inventory])
def call_all_inventory(session: Annotated[Session, Depends(get_session)]):
    return get_all_inventory(session)

@app.get("/manage-inventory/{inventory_id}", response_model=Inventory)
def get_single_inventory(inventory_id: int, session: Annotated[Session, Depends(get_session)]):
    return get_inventory_by_id(inventory_id=inventory_id, session=session)
