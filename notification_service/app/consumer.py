# notification_service/app/consumer.py
from aiokafka import AIOKafkaConsumer
import aiohttp

import asyncio
import json
from app.mailer import send_email
import requests

async def consume_order_topic():
    consumer = AIOKafkaConsumer(
        'order_topic',
        bootstrap_servers='broker:19092',
        group_id='notification_group'
    )

    await consumer.start()
    try:
        async for message in consumer:
            order_data = json.loads(message.value.decode('utf-8'))
            order_id = order_data['order_id']
            user_id = order_data['user_id']
            order_status = order_data['order_status']

            # Fetch user email from user_service
            user_email = await fetch_user_email(user_id)

            # Prepare the email content
            email_data = {
                "to": [user_email],
                "subject": f"Order Update: {order_id}",
                "body": f"Hi {user_email},\n\nYour order with ID {order_id} is now {order_status}.\n\nThank you for shopping with us!"
            }

            # Send the email
            send_email(email_data)
    finally:
        await consumer.stop()

async def fetch_user_email(user_id: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://user_service/users/{user_id}') as response:
                response.raise_for_status()
                user_data = await response.json()
                return user_data.get('email')
    except Exception as e:
        print(f"Failed to fetch user email: {e}")
        return None
