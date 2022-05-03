import os
import logging

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))

RABBITMQ_URL = os.getenv('RABBITMQ_URL')
EXCHANGE = os.getenv('EXCHANGE', 'logs')
QUEUE = os.getenv('QUEUE')
MESSAGE_TTL_MS = 2 * 60 * 1000
