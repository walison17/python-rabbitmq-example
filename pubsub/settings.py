import os


RABBITMQ_URL = os.getenv('RABBITMQ_URL')
EXCHANGE = os.getenv('EXCHANGE', 'logs')
QUEUE = os.getenv('QUEUE')
