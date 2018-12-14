import os

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
QUEUES = ['default']
