import signal
import time
from random import random

import pika
from retry import retry

from . import rabbit, settings


def on_message(channel, method, properties, body):
    message = body.decode()
    if random() > 0.5:
        channel.basic_ack(method.delivery_tag)
        print(f'ACK  -> {message}')
    else:
        channel.basic_nack(method.delivery_tag, requeue=True)
        print(f'NACK -> {message}')


@retry(pika.exceptions.AMQPConnectionError, delay=2, jitter=(1, 3))
def consume():
    print('Waiting for messages. To exit press CTRL+C')

    connection = rabbit.connect('consumer')
    channel = rabbit.channel(connection)
    channel.basic_qos(prefetch_count=1)

    channel.exchange_declare(exchange=settings.EXCHANGE, exchange_type='fanout', durable=True)
    channel.queue_declare(queue=settings.QUEUE, durable=True)
    channel.queue_bind(exchange=settings.EXCHANGE, queue=settings.QUEUE)

    channel.basic_consume(queue=settings.QUEUE, on_message_callback=on_message)

    def shutdown_handler(signum, frame):
        channel.stop_consuming()
        connection.close()
        print('Gracefully shutdown')
        exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    channel.start_consuming()
    time.sleep(2)


if __name__ == '__main__':
    consume()
