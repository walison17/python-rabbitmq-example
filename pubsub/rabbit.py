import pika
import contextvars

from . import settings

_CONNECTIONS = {}
_CHANNELS = contextvars.ContextVar('channels', default=None)


def connect(name):
    conn = _CONNECTIONS.get(name)
    if conn and conn.is_open:
        return conn

    params = pika.URLParameters(settings.RABBITMQ_URL)
    params.heartbeat = 5 * 60
    conn = pika.BlockingConnection(params)
    _CONNECTIONS[name] = conn
    return conn


def channel(connection):
    chn = _CHANNELS.get()
    if chn and chn.is_open:
        return chn

    chn = connection.channel()
    _CHANNELS.set(chn)
    return chn
