from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
from app.models.product_model import Product, ProductUpdate
from app.crud.product_crud import add_new_product, update_product_by_id, delete_product_by_id
from app.deps import get_session, get_kafka_producer

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="my-product-consumer-group",
        enable_auto_commit=False  # Disable auto commit to handle state manually
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers
    )

    await consumer.start()
    await producer.start()
    try:
        async for message in consumer:
            product_data = json.loads(message.value.decode())
            product_id = product_data['product']['id']
            key = str(product_id).encode('utf-8')  # Unique key for each product

            with next(get_session()) as session:
                if product_data['action'] == 'create':
                    add_new_product(product_data=Product(**product_data['product']), session=session)
                    # Commit the creation to Kafka
                    await producer.send_and_wait(topic, message.value, key=key)
                elif product_data['action'] == 'update':
                    update_product_by_id(product_id=product_data['product']['id'], to_update_product_data=ProductUpdate(**product_data['product']), session=session)
                    # Update the existing message in Kafka
                    await producer.send_and_wait(topic, message.value, key=key)
                elif product_data['action'] == 'delete':
                    delete_product_by_id(product_id=product_data['product']['id'], session=session)
                    # Delete the message from Kafka by sending a tombstone record
                    await producer.send_and_wait(topic, None, key=key)

                # Commit the offset only after successful processing
                await consumer.commit()
    finally:
        await consumer.stop()
        await producer.stop()
