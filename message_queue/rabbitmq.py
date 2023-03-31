import time
import socket
import select
import logging
import umsgpack
import threading

import amqp
from urllib.parse import unquote
try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse
import queue as BaseQueue


def catch_error(func):
    """Catch errors of rabbitmq then reconnect"""
    import amqp
    try:
        import pika.exceptions
        connect_exceptions = (
            pika.exceptions.ConnectionClosed,
            pika.exceptions.AMQPConnectionError,
        )
    except ImportError:
        connect_exceptions = ()

    connect_exceptions += (
        select.error,
        socket.error,
        amqp.ConnectionError
    )

    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except connect_exceptions as e:
            logging.error('RabbitMQ error: %r, reconnect.', e)
            self.reconnect()
            return func(self, *args, **kwargs)
    return wrap


class PikaQueue(object):
    """
    A Queue like rabbitmq connector
    """

    Empty = BaseQueue.Empty
    Full = BaseQueue.Full
    max_timeout = 0.3

    def __init__(self, names, amqp_url='amqp://guest:guest@localhost:5672/%2F',
                 maxsize=0, lazy_limit=True):
        """
        Constructor for a PikaQueue.

        amqp_url:   https://www.rabbitmq.com/uri-spec.html
        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: as rabbitmq is shared between multipul instance, for a strict
                    limit on the number of items in the queue. PikaQueue have to
                    update current queue size before every put operation. When
                    `lazy_limit` is enabled, PikaQueue will check queue size every
                    max_size / 10 put operation for better performace.
        """
        self.names = names
        self.amqp_url = amqp_url
        self.maxsize = maxsize
        self.lock = threading.RLock()

        self.lazy_limit = lazy_limit
        if self.lazy_limit and self.maxsize:
            self.qsize_diff_limit = int(self.maxsize * 0.1)
        else:
            self.qsize_diff_limit = 0
        self.qsize_diff = 0

        self.reconnect()

    def reconnect(self):
        """Reconnect to rabbitmq server"""
        import pika
        import pika.exceptions

        self.connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
        self.channel = self.connection.channel()
        try:
            self.put_channel = self.connection.channel()
            self.get_channel = self.connection.channel()
        except pika.exceptions.ChannelClosed:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
            self.put_channel = self.connection.channel()
            self.get_channel = self.connection.channel()
        for name in self.names:

            self.put_channel.queue_declare(name,durable=True)
            self.get_channel.queue_declare(name,durable=True)
        #self.channel.queue_purge(self.name)

    @catch_error
    def qsize(self, name):
        with self.lock:
            ret = self.get_channel.queue_declare(name, durable=True,passive=True)
        return ret.method.message_count

    def empty(self, name):
        if self.qsize(name) == 0:
            return True
        else:
            return False

    def full(self, name):
        if self.maxsize and self.qsize(name) >= self.maxsize:
            return True
        else:
            return False

    @catch_error
    def put(self,name, obj, block=True, timeout=None):
        if not block:
            return self.put_nowait(name, obj)

        start_time = time.time()
        while True:
            try:
                return self.put_nowait(name, obj)
            except BaseQueue.Full:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

    @catch_error
    def put_nowait(self, name, obj):
        from pika import BasicProperties
        if self.lazy_limit and self.qsize_diff < self.qsize_diff_limit:
            pass
        elif self.full(name):
            raise BaseQueue.Full
        else:
            self.qsize_diff = 0
        with self.lock:
            self.qsize_diff += 1
            return self.put_channel.basic_publish("", name, umsgpack.packb(obj),properties=BasicProperties(delivery_mode = 2))

    @catch_error
    def get(self, name, block=True, timeout=None, ack=False, ):
        if not block:
            return self.get_nowait(name)

        start_time = time.time()
        while True:
            try:
                return self.get_nowait(name, ack)
            except BaseQueue.Empty:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

    @catch_error
    def get_nowait(self, name, ack=False):
        with self.lock:
            method_frame, header_frame, body = self.get_channel.basic_get(name, not ack)
            if method_frame is None:
                raise BaseQueue.Empty
            if ack:
                self.get_channel.basic_ack(method_frame.delivery_tag)
        return umsgpack.unpackb(body)

    @catch_error
    def delete(self,name):
        with self.lock:
            return self.put_channel.queue_delete(queue=name)


class AmqpQueue(PikaQueue):
    Empty = BaseQueue.Empty
    Full = BaseQueue.Full
    max_timeout = 0.3

    def __init__(self, names, amqp_url='amqp://guest:guest@localhost:5672/%2F',
                 maxsize=0, lazy_limit=True):
        """
        Constructor for a AmqpQueue.

        amqp_url:   https://www.rabbitmq.com/uri-spec.html
        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: as rabbitmq is shared between multipul instance, for a strict
                    limit on the number of items in the queue. PikaQueue have to
                    update current queue size before every put operation. When
                    `lazy_limit` is enabled, PikaQueue will check queue size every
                    max_size / 10 put operation for better performace.
        """
        self.names = names
        self.amqp_url = amqp_url
        self.maxsize = maxsize
        self.lock = threading.RLock()

        self.lazy_limit = lazy_limit
        if self.lazy_limit and self.maxsize:
            self.qsize_diff_limit = int(self.maxsize * 0.1)
        else:
            self.qsize_diff_limit = 0
        self.qsize_diff = 0

        self.reconnect()

    def reconnect(self):
        """Reconnect to rabbitmq server"""
        parsed = urlparse.urlparse(self.amqp_url)
        port = parsed.port or 5672
        self.connection = amqp.Connection(host="%s:%s" % (parsed.hostname, port),
                                          userid=parsed.username or 'guest',
                                          password=parsed.password or 'guest',
                                          virtual_host=unquote(
                                              parsed.path.lstrip('/') or '%2F'))
        self.put_channel = self.connection.channel()
        self.get_channel = self.connection.channel()
        try:
            for name in self.names:
                self.put_channel.queue_declare(name,durable=True)
                self.get_channel.queue_declare(name,durable=True)
        except amqp.exceptions.PreconditionFailed:
            pass
        #self.channel.queue_purge(self.name)

    @catch_error
    def qsize(self,qname):
        with self.lock:
            name, message_count, consumer_count = self.get_channel.queue_declare(
                qname, passive=True)
        return message_count

    @catch_error
    def put_nowait(self, name, obj):
        if self.lazy_limit and self.qsize_diff < self.qsize_diff_limit:
            pass
        elif self.full(name):
            raise BaseQueue.Full
        else:
            self.qsize_diff = 0
        with self.lock:
            self.qsize_diff += 1
            msg = amqp.Message(umsgpack.packb(obj))
            return self.put_channel.basic_publish(msg, exchange="", routing_key=name)

    @catch_error
    def get_nowait(self, name, ack=False):
        with self.lock:
            message = self.get_channel.basic_get(name, not ack)
            if message is None:
                raise BaseQueue.Empty
            if ack:
                self.get_channel.basic_ack(message.delivery_tag)
        return umsgpack.unpackb(message.body)

Queue = AmqpQueue
