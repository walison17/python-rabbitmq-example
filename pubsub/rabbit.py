import pika
import contextvars

from . import settings

_CONNECTIONS = {}
_CHANNELS = contextvars.ContextVar('channels', default={})


class NamedBlockingConnection(pika.BlockingConnection):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


def connect(name):
    conn = _CONNECTIONS.get(name)
    if conn and conn.is_open:
        return conn

    params = pika.URLParameters(settings.RABBITMQ_URL)
    params.heartbeat = 5 * 60
    conn = NamedBlockingConnection(name, params)
    _CONNECTIONS[name] = conn
    return conn


def channel(connection):
    channels = _CHANNELS.get()
    chn = channels.get(connection.name)
    if chn and chn.is_open:
        return chn

    chn = connection.channel()
    channels[connection.name] = chn
    _CHANNELS.set(channels)
    return chn
