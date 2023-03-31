def connect_cache(name="", host=None, password="", port=5672, db=0):
    """
    create connection to message queue

    db:
        database index number
        
    builtin:
        None
    """

    
    if host:
        from .redis_cache import Cache
        return Cache(name=name, host=host, password=password, port=port, db=db)
    else:
        return set()