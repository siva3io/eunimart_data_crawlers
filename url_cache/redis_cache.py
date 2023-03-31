import time
import socket
import select
import logging
import threading
import redis 
from urllib.parse import unquote
try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse

def catch_error(func):
    """Catch errors of redis then reconnect"""

    connect_exceptions = (
        select.error,
        socket.error,
        redis.ConnectionError,
        redis.RedisError,
        redis.TimeoutError
    )

    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except connect_exceptions as e:
            time.sleep(0.5)
            logging.error('Redis error: %r, reconnect.', e)
            self.connect()
            return func(self, *args, **kwargs)
    return wrap


class RedisCache(object):
    

    def __init__(self, name="", host="localhost", password="", port=5672, db=0):
        self.name = name
        self.host = host
        self.password = password
        self.port = port
        self.db = db
        self.lock = threading.RLock()
        self.connect()

    @catch_error
    def connect(self):
        self.connection = redis.StrictRedis(
            host = self.host,
            password = self.password, 
            port = self.port, 
            db = self.db
            )

    @catch_error
    def get(self, key):
        with self.lock:
            value = self.connection.get(key)
        return value

    @catch_error
    def set(self, key, value, expires=43200):
        with self.lock:
            val = self.connection.set(key, value, ex=expires)
        return val




Cache = RedisCache