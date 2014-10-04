# coding=utf-8
"""Environment"""

from logging import getLogger
from logging.config import dictConfig
import os
from pkg_resources import resource_filename
import yaml
import uuid

from easydict import EasyDict

from utils.decorators import cached_property


class Config(object):
    def __init__(self, filename):
        self._conf_filename = filename

    @cached_property
    def config(self):
        with open(self._conf_filename) as config_f:
            config = EasyDict(yaml.load(config_f))
            config.process_uuid = uuid.uuid4().hex
            dictConfig(config.logging)
            getLogger(__name__).debug(
                'Configuration for %s loaded from %s.',
                config.process_uuid[:8],
                self._conf_filename)
        return config


CFG = Config(os.environ.get('SLIPPER_CONFIG',
                            resource_filename(__package__,
                                              'etc/conf.yaml'))).config
