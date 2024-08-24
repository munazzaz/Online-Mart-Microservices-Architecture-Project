import asyncio
from aiokafka import AIOKafkaConsumer
from email.message import EmailMessage
import aiosmtplib
from app.settings import BOOTSTRAP_SERVER, KAFKA_USER_TOPIC, KAFKA_ORDER_CREATED_TOPIC, KAFKA_ORDER_UPDATED_TOPIC, KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL

async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    
    await aiosmtplib.send(
        message,
        hostname=SMTP_SERVER,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
    )

async def consume_and_notify():
    consumer = AIOKafkaConsumer(
        KAFKA_USER_TOPIC, 
        KAFKA_ORDER_CREATED_TOPIC,
        KAFKA_ORDER_UPDATED_TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVER,
        group_id=KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION
    )
    
    await consumer.start()
    try:
        async for message in consumer:
            topic = message.topic
            data = message.value

            if topic == KAFKA_USER_TOPIC:
                # Assuming the message contains a user object with email
                user_email = data.get('email')
                user_id = data.get('id')
            
            elif topic in [KAFKA_ORDER_CREATED_TOPIC, KAFKA_ORDER_UPDATED_TOPIC]:
                order_id = data.get('order_id')
                order_status = data.get('status')
                user_id = data.get('user_id')

                # Email to the user
                if user_id and user_email:
                    subject = f"Order {order_id} - Status Update"
                    body = f"Your order with ID {order_id} is now {order_status}."
                    await send_email(user_email, subject, body)
    finally:
        await consumer.stop()

async def main():
    await consume_and_notify()
