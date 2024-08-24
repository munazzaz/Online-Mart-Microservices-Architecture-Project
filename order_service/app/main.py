from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends
from sqlmodel import Session, SQLModel
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import settings
from app.db_engine import engine
from app.models.order_model import Order, OrderUpdate, OrderCreate
from app.crud.order_crud import create_order, get_order_by_id, update_order_by_id, delete_order_by_id
from app.deps import get_http_client, get_session, get_kafka_producer

from fastapi import HTTPException, status
from httpx import AsyncClient

# In this order are created successfully

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=settings.KAFKA_CONSUMER_GROUP_ID_FOR_ORDER
    )
    await consumer.start()
    try:
        async for message in consumer:
            order_data = json.loads(message.value.decode())
            with next(get_session()) as session:
                if order_data['action'] == 'create':
                    create_order(order_data=Order(**order_data['order']), session=session)
                elif order_data['action'] == 'update':
                    update_order_by_id(order_id=order_data['order']['id'], to_update_order_data=OrderUpdate(**order_data['order']), session=session)
                elif order_data['action'] == 'delete':
                    delete_order_by_id(order_id=order_data['order']['id'], session=session)
    finally:
        await consumer.stop()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    consumer_task = asyncio.create_task(consume_messages(settings.KAFKA_ORDER_TOPIC, settings.BOOTSTRAP_SERVER))
    try:
        yield
    finally:
        consumer_task.cancel()
        await consumer_task

app = FastAPI(
    lifespan=lifespan,
    title="Order Service API",
    version="0.0.1",
    description = "The Order Service API is a robust backend solution designed to manage and process customer orders efficiently.",
    servers=[
        {
            "url": "http://127.0.0.1:8006/",
            "description": "Local Development Server"
        }
        ]
)



@app.post("/manage-orders/", response_model=Order)
async def create_new_order(
    order_create: OrderCreate, 
    session: Session = Depends(get_session), 
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    client: AsyncClient = Depends(get_http_client)
):
    try:
        # Verify if the user exists in user_service
        user_response = await client.get(f"http://user_service:8000/users/{order_create.user_id}")
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User does not exist"
            )
        
        # Fetch product details from product_service
        product_response = await client.get(f"http://product_service:8000/manage-products/{order_create.product_id}")
        
        if product_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product does not exist"
            )

        product_data = product_response.json()
        print("Product data fetched:", product_data)

        # Validate the product name with case insensitivity
        provided_product_name = order_create.product_name.strip().lower()
        actual_product_name = product_data['name'].strip().lower()

        if provided_product_name != actual_product_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provided product name does not match the actual product name."
            )

        # Fetch inventory details from inventory_service
        inventory_response = await client.get(f"http://inventory_service:8000/manage-inventory/product/{order_create.product_id}")
        
        if inventory_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inventory information could not be retrieved"
            )

        inventory_data = inventory_response.json()
        available_quantity = inventory_data['quantity']

        # Check if the ordered quantity exceeds the available stock
        if order_create.quantity > available_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ordered quantity ({order_create.quantity}) exceeds available stock ({available_quantity})"
            )

        # Calculate total price
        total_price = product_data['price'] * order_create.quantity

        # Create the order dictionary with additional fields
        order_dict = order_create.dict()
        order_dict['product_name'] = product_data['name']
        order_dict['total_price'] = total_price
        order_dict['status'] = 'pending'
        order_dict['created_at'] = datetime.utcnow()
        order_dict['updated_at'] = datetime.utcnow()

        # Convert datetime fields to strings
        order_dict['created_at'] = order_dict['created_at'].isoformat()
        order_dict['updated_at'] = order_dict['updated_at'].isoformat()

        # Log the order data before sending to Kafka
        print("Order to be sent to Kafka:", order_dict)

        # Send the order creation message to Kafka
        order_json = json.dumps({'action': 'create', 'order': order_dict}).encode("utf-8")
        key = str(order_create.id).encode('utf-8')
        await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, order_json, key=key)

        # Save the order to the database
        new_order = Order(**order_dict)
        session.add(new_order)
        session.commit()
        session.refresh(new_order)
        
        return new_order

    except HTTPException as http_exc:
        # Handle known HTTP exceptions
        print(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc
    except Exception as exc:
        # Log and raise unexpected errors
        print(f"Unexpected error occurred: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the order"
        )


@app.patch("/manage-orders/{order_id}", response_model=Order)
async def update_single_order(
    order_id: int, 
    order: OrderUpdate, 
    session: Session = Depends(get_session), 
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    client: AsyncClient = Depends(get_http_client)
):
    try:
        # Fetch the existing order
        existing_order = session.get(Order, order_id)
        if not existing_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Order not found"
            )

        # Validate and update product_id if provided
        if order.product_id is not None:
            product_response = await client.get(f"http://product_service:8000/manage-products/{order.product_id}")
            if product_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product does not exist"
                )

            product_data = product_response.json()

            if order.product_name is not None:
                provided_product_name = order.product_name.strip().lower()
                actual_product_name = product_data['name'].strip().lower()

                if provided_product_name != actual_product_name:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Provided product name does not match the actual product name."
                    )

            # Fetch inventory details if quantity is being updated
            if order.quantity is not None:
                inventory_response = await client.get(f"http://inventory_service:8000/manage-inventory/product/{order.product_id}")
                if inventory_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Inventory information could not be retrieved"
                    )

                inventory_data = inventory_response.json()
                available_quantity = inventory_data['quantity']

                if order.quantity > available_quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ordered quantity ({order.quantity}) exceeds available stock ({available_quantity})"
                    )

            # Update the order fields
            if order.product_name is not None:
                existing_order.product_name = product_data['name']
            if order.quantity is not None:
                existing_order.quantity = order.quantity
                existing_order.total_price = product_data['price'] * order.quantity
            existing_order.product_id = order.product_id

        # Commit changes to the database
        session.add(existing_order)
        session.commit()
        session.refresh(existing_order)

        # Prepare the order data for Kafka
        order_dict = {
            'product_id': existing_order.product_id,
            'product_name': existing_order.product_name,
            'quantity': existing_order.quantity,
            'total_price': existing_order.total_price,
            'id': existing_order.id,
            # 'status': existing_order.status,
            'created_at': existing_order.created_at.isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        order_json = json.dumps({'action': 'update', 'order': order_dict}).encode("utf-8")
        key = str(order_id).encode('utf-8')
        await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, order_json, key=key)

        return existing_order

    except HTTPException as http_exc:
        # Handle known HTTP exceptions
        print(f"HTTPException occurred: {http_exc.detail}")
        raise http_exc
    except Exception as exc:
        # Log and raise unexpected errors
        print(f"Unexpected error occurred: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the order"
        )


@app.delete("/manage-orders/{order_id}", response_model=dict)
async def delete_single_order(order_id: int, session: Session = Depends(get_session), producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    # Check if the order exists before deleting
    order = get_order_by_id(order_id=order_id, session=session)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} does not exist"
        )
    
    # If the order exists, proceed to delete it
    delete_order_by_id(order_id=order_id, session=session)
    
    # Send the deletion event to Kafka
    order_json = json.dumps({'action': 'delete', 'order': {'id': order_id}}).encode("utf-8")
    key = str(order_id).encode('utf-8')
    await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, order_json, key=key)
    
    return {"message": "Order Deleted Successfully"}


@app.get("/manage-orders/{order_id}", response_model=Order)
def get_single_order(order_id: int, session: Session = Depends(get_session)):
    try:
        # Fetch the order by ID
        order = get_order_by_id(order_id=order_id, session=session)
        
        # Check if the order exists
        if not order:
            # Raise an error if the order does not exist
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} does not exist"
            )
        
        return order

    except HTTPException as http_exc:
        # Re-raise known HTTP exceptions so they are properly handled
        raise http_exc
    except Exception as exc:
        # Log unexpected exceptions
        print(f"Unexpected error occurred: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request"
        )









