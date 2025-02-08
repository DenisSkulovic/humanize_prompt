import aio_pika
import asyncio
from core.config import Config

class MessageQueueService:
    """
    A generic messaging queue service that abstracts RabbitMQ interactions using async/await.
    """
    def __init__(self):
        self.host = Config.RABBITMQ_HOST
        self.port = Config.RABBITMQ_PORT

    async def publish(self, queue_name: str, message: str):
        """
        Publishes a message to the queue asynchronously.
        """
        connection = None
        channel = None
        try:
            connection = await aio_pika.connect_robust(Config.RABBITMQ_URL)
            channel = await connection.channel()

            await channel.declare_queue(queue_name, durable=True)
            exchange = channel.default_exchange  # ✅ Access as an attribute, not a method
            await exchange.publish(
                aio_pika.Message(body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue_name,
            )
        finally:
            if connection:
                await connection.close()
            if channel:
                await channel.close()

    async def consume(self, queue_name: str):
        """
        Consumes messages from the queue asynchronously as an async generator.
        """
        connection = None
        channel = None
        try:
            connection = await aio_pika.connect_robust(f"amqp://{self.host}:{self.port}")
            channel = await connection.channel()

            await channel.declare_queue(queue_name, durable=True)

            queue = await channel.get_queue(queue_name)
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        yield message.body.decode()
        finally:
            if connection:
                await connection.close()
            if channel:
                await channel.close()
