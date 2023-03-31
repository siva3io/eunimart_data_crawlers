try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse


def connect_message_queue(names, url=None, maxsize=0, lazy_limit=True):
    """
    create connection to message queue

    name:
        name of message queues

    rabbitmq:
        amqp://username:password@host:5672/%2F
        see https://www.rabbitmq.com/uri-spec.html
    builtin:
        None
    """

    parsed = urlparse.urlparse(url)
    if parsed.scheme == 'amqp':
        from .rabbitmq import Queue
        return Queue(names, url, maxsize=maxsize, lazy_limit=lazy_limit)
    elif parsed.scheme == 'beanstalk':
        from .beanstalk import Queue
        return Queue(names, host=parsed.netloc, maxsize=maxsize)

    else:
        raise Exception('unknown connection url: %s', url)
