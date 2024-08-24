import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlmodel import Session, SQLModel
from stripe.error import StripeError
import stripe
import json

from app import settings
from app.db_engine import engine
from app.models.payment_model import Payment
from app.crud.payment_crud import create_payment, get_payment_by_order_id, update_payment_status
from app.deps import get_session, get_kafka_producer

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    try:
        yield
    finally:
        pass

app = FastAPI(
    lifespan=lifespan,
    title="Payment Service API",
    version="0.0.1",
    description = "The Payment Service API is designed to seamlessly manage and process payments for your orders.",
    servers=[
        {
            "url": "http://127.0.0.1:8010/",
            "description": "Local Development Server"
        }
        ]
    
)

@app.post("/process-payment/")
async def process_payment(order_id: int, session: Session = Depends(get_session), producer = Depends(get_kafka_producer)):
    order_response = await verify_order(order_id)
    
    if not order_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found for payment")
    
    new_payment = Payment(
        order_id=order_id,
        product_name=order_response['product_name'],
        quantity=order_response['quantity'],
        total_price=order_response['total_price'],  # Assuming this is already multiplied by quantity
        status='Pending'
    )
    
    create_payment(payment_data=new_payment, session=session)
    
    try:
        # Here, unit_amount is the total price already calculated
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': new_payment.product_name,
                    },
                    'unit_amount': int(new_payment.total_price * 100),  # Use the pre-calculated total price
                },
                'quantity': 1,  # Set quantity to 1 to avoid additional multiplication
            }],
            mode='payment',
            success_url=f'{settings.BASE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{settings.BASE_URL}/cancel',
        )
        
        # Publish Kafka event
        payment_event = {
            "payment_id": new_payment.id,
            "order_id": new_payment.order_id,
            "product_name": new_payment.product_name,
            "quantity": new_payment.quantity,
            "total_price": new_payment.total_price,
            "status": "Pending"
        }
        await producer.send_and_wait(settings.KAFKA_PAYMENT_TOPIC, json.dumps(payment_event).encode('utf-8'))
        
        return {
            "payment_id": new_payment.id,
            "status": "Payment pending",
            "checkout_url": checkout_session.url,
            "order_id": new_payment.order_id,
            "product_name": new_payment.product_name,
            "quantity": new_payment.quantity,
            "total_price": new_payment.total_price
        }
    except StripeError as e:
        update_payment_status(payment_id=new_payment.id, status="Failed", session=session)
        
        # Publish Kafka event
        payment_event = {
            "payment_id": new_payment.id,
            "order_id": new_payment.order_id,
            "product_name": new_payment.product_name,
            "quantity": new_payment.quantity,
            "total_price": new_payment.total_price,
            "status": "Payment Failed",
            "error": str(e)
        }
        await producer.send_and_wait(settings.KAFKA_PAYMENT_TOPIC, json.dumps(payment_event).encode('utf-8'))
        
        return {
            "payment_id": new_payment.id,
            "status": "Payment failed",
            "error": str(e),
            "order_id": new_payment.order_id,
            "product_name": new_payment.product_name,
            "quantity": new_payment.quantity,
            "total_price": new_payment.total_price
        }


@app.get("/success", include_in_schema=False)
async def payment_success(request: Request, session: Session = Depends(get_session), producer = Depends(get_kafka_producer)):
    session_id = request.query_params.get('session_id')
    if not session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session ID not provided")

    try:
        # Retrieve the checkout session and payment intent from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)

        # Retrieve payment record from the database
        payment = get_payment_by_order_id(order_id=checkout_session.client_reference_id, session=session)
        if payment:
            # Update payment status in the database
            update_payment_status(payment_id=payment.id, status="Successful", session=session)
            
            # Publish Kafka event with updated "Successful" status
            payment_event = {
                "payment_id": payment.id,
                "order_id": payment.order_id,
                "product_name": payment.product_name,
                "quantity": payment.quantity,
                "total_price": payment.total_price,
                "status": "Successful"
            }
            await producer.send_and_wait(settings.KAFKA_PAYMENT_TOPIC, json.dumps(payment_event).encode('utf-8'))
        
        return {"message": "Payment successful!", "payment_details": payment_intent}
    except StripeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/cancel", include_in_schema=False)
async def payment_cancel(request: Request, session: Session = Depends(get_session), producer = Depends(get_kafka_producer)):
    session_id = request.query_params.get('session_id')
    if not session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session ID not provided")

    # Retrieve the payment record by session_id if needed or identify the payment_id
    # If payment_id is known, update the record accordingly

    # Publish Kafka event for canceled payment
    payment_event = {
        "payment_id": None,  # No payment ID for canceled payments
        "order_id": None,    # No order ID for canceled payments
        "product_name": None,
        "quantity": None,
        "total_price": None,
        "status": "Canceled"
    }
    await producer.send_and_wait(settings.KAFKA_PAYMENT_TOPIC, json.dumps(payment_event).encode('utf-8'))

    return {"message": "Payment was canceled. Please try again if you wish to complete the purchase."}


@app.get("/payments/{order_id}", response_model=Payment)
async def get_payment_status(order_id: int, session: Session = Depends(get_session)):
    payment = get_payment_by_order_id(order_id=order_id, session=session)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found for the order")
    return payment

async def verify_order(order_id: int):
    order_service_url = f"http://order_service:8000/manage-orders/{order_id}"
    response = await make_http_request(order_service_url)
    return response

async def make_http_request(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
