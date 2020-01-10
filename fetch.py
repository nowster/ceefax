#!/usr/bin/python3
import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
import pickle

import config
config=config.Config().config

class _Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class Fetcher(metaclass=_Singleton):
    def __init__(self):
        cachefile = f"{config['cachedir']}/requests"
        self._cached_sess = CacheControl(requests.Session(),
                                         cache=FileCache(cachefile))

        self.head = self._cached_sess.head
        self.get = self._cached_sess.get
