# coding=utf-8
"""Environment"""

from logging import getLogger
from logging.config import dictConfig
from pkg_resources import resource_filename
import yaml
import uuid


__all__ = ['CFG', 'getLogger']


class _Config(dict):

    __config__ = None

    def __call__(self, filename=None):
        if self.__config__ is not None:
            raise AttributeError('Already configured with %s.'
                                 % self.__config__)
        filename = filename or resource_filename(__package__, 'etc/conf.yaml')
        self.__config__ = filename
        with open(filename) as config_f:
            self.__init__(yaml.load(config_f))
            self.process_uuid = uuid.uuid4().hex
            dictConfig(self.logging)
            getLogger(__name__).debug(
                'Configuration for %s loaded from %s.',
                self.process_uuid[:8],
                filename)

    def __init__(self, d=None):
        super(_Config, self).__init__()
        if d is None:
            d = {}
        for k, v in d.items():
            setattr(self, k, v)
        # Class attributes
        for k in self.__class__.__dict__.keys():
            if not (k.startswith('__') and k.endswith('__')):
                setattr(self, k, getattr(self, k))

    def __setattr__(self, name, value):
        if isinstance(value, (list, tuple)):
            value = [self.__class__(x) if isinstance(x, dict)
                     else x for x in value]
        else:
            value = self.__class__(value) if isinstance(value, dict) else value
        super(_Config, self).__setattr__(name, value)
        self[name] = value


CFG = _Config()
