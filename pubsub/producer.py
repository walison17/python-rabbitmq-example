import signal
import time

import pika
from retry import retry

from . import rabbit, settings


@retry(pika.exceptions.AMQPConnectionError, delay=2, jitter=(1, 3))
def produce():
    connection = rabbit.connect('producer')
    channel = rabbit.channel(connection)

    def shutdown_handler(signum, frame):
        print('Gracefully shutdown')
        connection.close()
        exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    channel.exchange_declare(
        exchange=settings.EXCHANGE, exchange_type='fanout', durable=True
    )

    count = 1
    while True:
        message = f'log{count}'
        channel.basic_publish(
            exchange=settings.EXCHANGE,
            routing_key='',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        print(f'Published message: {message}')
        count += 1
        time.sleep(2)


if __name__ == '__main__':
    produce()
