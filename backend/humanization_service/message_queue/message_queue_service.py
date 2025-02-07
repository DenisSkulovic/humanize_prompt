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
        self.queue_name = Config.RABBITMQ_QUEUE
        self.connection = None
        self.channel = None

    async def connect(self):
        """
        Establishes an asynchronous connection to RabbitMQ.
        """
        self.connection = await aio_pika.connect_robust(f"amqp://{self.host}:{self.port}")
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(self.queue_name, durable=True)

    async def publish(self, message: str):
        """
        Publishes a message to the queue asynchronously.
        """
        if not self.channel:
            await self.connect()
        exchange = await self.channel.default_exchange()
        await exchange.publish(
            aio_pika.Message(body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=self.queue_name,
        )

    async def consume(self, callback):
        """
        Starts consuming messages from the queue asynchronously with a given callback.
        """
        if not self.channel:
            await self.connect()
        queue = await self.channel.get_queue(self.queue_name)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await callback(message.body.decode())

    async def close(self):
        """
        Closes the connection to RabbitMQ.
        """
        if self.connection:
            await self.connection.close()