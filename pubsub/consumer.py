import signal
import time
import logging
import json
from random import random

import pika
from retry import retry

from . import rabbit, settings

logger = logging.getLogger(__name__)


def echo(channel, method, properties, body):
    user = json.loads(body)
    if random() > 0.5:
        channel.basic_ack(method.delivery_tag)
        logger.info(f'ACK  -> {user}')
    else:
        channel.basic_nack(method.delivery_tag, requeue=True)
        logger.info(f'NACK -> {user}')
    time.sleep(3 * random())


HANDLERS = {'user.created': echo}


def on_message(channel, method, properties, body):
    try:
        handler = HANDLERS[properties.type]
    except KeyError:
        logger.exception('Unknown event')
    else:
        handler(channel, method, properties, body)


@retry(pika.exceptions.AMQPConnectionError, delay=2, jitter=(1, 3))
def consume():
    logger.info('Waiting for messages. To exit press CTRL+C')

    connection = rabbit.connect()
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    channel.exchange_declare(
        exchange=settings.EXCHANGE, exchange_type='fanout', durable=True
    )
    channel.queue_declare(
        queue=settings.QUEUE,
        durable=True,
        arguments={'x-message-ttl': settings.MESSAGE_TTL_MS},
    )
    channel.queue_bind(exchange=settings.EXCHANGE, queue=settings.QUEUE)

    channel.basic_consume(queue=settings.QUEUE, on_message_callback=on_message)

    def shutdown_handler(signum, frame):
        logger.info('Gracefully shutdown')
        channel.stop_consuming()
        connection.close()
        raise SystemExit

    signal.signal(signal.SIGTERM, shutdown_handler)

    channel.start_consuming()


if __name__ == '__main__':
    consume()
