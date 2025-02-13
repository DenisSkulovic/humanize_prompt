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

    async def send_message(self, queue_name: str, message: str):
        """
        Publishes a message to the queue asynchronously.
        """
        connection = None
        channel = None
        try:
            connection = await aio_pika.connect_robust(Config.RABBITMQ_URL)
            channel = await connection.channel()

            await channel.declare_queue(queue_name, durable=True)
            exchange = channel.default_exchange
            await exchange.publish(
                aio_pika.Message(body=message.encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue_name,
            )
        finally:
            if connection:
                await connection.close()
            if channel:
                await channel.close()

    async def get_next_message(self, queue_name: str):
        """
        Consumes messages from the queue asynchronously as an async generator.
        """
        connection = None
        channel = None
        try:
            connection = await aio_pika.connect_robust(Config.RABBITMQ_URL)
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

    async def get_queue_length(self, queue_name: str) -> int:
        """
        Returns the number of messages currently in the specified RabbitMQ queue.
        """
        connection = None
        channel = None
        try:
            connection = await aio_pika.connect_robust(Config.RABBITMQ_URL)
            channel = await connection.channel()

            queue = await channel.declare_queue(queue_name, durable=True)
            return queue.declaration_result.message_count

        finally:
            if connection:
                await connection.close()
            if channel:
                await channel.close()

    async def delete_queue(self, queue_name: str):
        """
        Deletes a queue after processing is complete.
        """
        connection = None
        channel = None
        try:
            connection = await aio_pika.connect_robust(Config.RABBITMQ_URL)
            channel = await connection.channel()
            await channel.queue_delete(queue_name)  # ✅ Manually delete queue
            print(f"✅ Queue {queue_name} deleted")
        finally:
            if connection:
                await connection.close()
            if channel:
                await channel.close()

