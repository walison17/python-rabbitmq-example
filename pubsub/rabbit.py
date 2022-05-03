import pika

from . import settings


def connect():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    params.heartbeat = 5 * 60
    conn = pika.BlockingConnection(params)
    return conn
