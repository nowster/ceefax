#!/usr/bin/python3
import yaml

_default_config_file = 'teletext.yaml'

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

class Config(metaclass=_Singleton):
    def __init__(self, config=_default_config_file):
        self._config_file = config
        self._config = {}
        self.reload()

    def reload(self):
        print("Load config")
        try:
            with open(self._config_file, 'r') as f:
                c = yaml.safe_load(f)
                self._config = c
        except yaml.YAMLError as exc:
            print("Error in configuration file:", exc, flush=True)
            if not self._config:
                raise

    @property
    def config(self):
        return self._config
