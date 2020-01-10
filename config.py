#!/usr/bin/python3
import yaml

_default_config_file = 'defaults.yaml'

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
    def __init__(self):
        self._config_files = []
        self._config = {}

    def add(self, config=_default_config_file):
        self._config_files.append(config)

    def load(self):
        print("Load config")
        new = dict()
        for f in self._config_files:
            try:
                with open(f, 'r') as f:
                    c = yaml.safe_load(f)
                    if c:
                        new.update(c)
            except yaml.YAMLError as exc:
                print("Error in configuration file:", exc, flush=True)
                if not self._config:
                    raise

        # Assignment will invalidate copies of the singleton.
        # Avoid it.
        self._config.clear()
        self._config.update(new)

    @property
    def config(self):
        return self._config
