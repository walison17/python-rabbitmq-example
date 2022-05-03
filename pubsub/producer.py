import json
import logging
import random
import signal
import time
import uuid

import pika
from faker import Faker
from retry import retry

from . import rabbit, settings

logger = logging.getLogger(__name__)

faker = Faker('pt_BR')


@retry(pika.exceptions.AMQPConnectionError, delay=2, jitter=(1, 3))
def produce():
    connection = rabbit.connect()
    channel = connection.channel()

    def shutdown_handler(signum, frame):
        logger.info('Gracefully shutdown')
        connection.close()
        raise SystemExit

    signal.signal(signal.SIGTERM, shutdown_handler)

    channel.exchange_declare(
        exchange=settings.EXCHANGE, exchange_type='fanout', durable=True
    )

    while True:
        user = {
            'name': faker.name(),
            'email': faker.email(),
            'cpf': faker.cpf(),
        }
        message_id = uuid.uuid4()
        channel.basic_publish(
            exchange=settings.EXCHANGE,
            routing_key='',
            body=json.dumps(user),
            properties=pika.BasicProperties(
                message_id=str(message_id),
                type='user.created',
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                content_type='application/json',
                timestamp=int(time.time()),
            ),
        )
        logger.info(f'Published message: {message_id}')
        time.sleep(5 * random.random())


if __name__ == '__main__':
    produce()
