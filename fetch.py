#!/usr/bin/python3
import requests
from cachecontrol import CacheControl # type: ignore
from cachecontrol.caches.file_cache import FileCache # type: ignore
import sys
import time

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

    def get(self, *args, **kwargs):
        try:
            return self._cached_sess.get(*args, **kwargs)
        except requests.exceptions.Timeout as errc:
            print ("Timeout:",errc)
            time.sleep(1)
            return self.get(*args, **kwargs)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            time.sleep(1)
            return self.get(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print(e, flush=True)
            sys.exit(1)
