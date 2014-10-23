# coding=utf-8

from abc import ABCMeta, abstractmethod

from six import with_metaclass

from slipper.env import CFG
from slipper.utils.imports import class_for_name


class AbstractDriver(with_metaclass(ABCMeta)):

    @abstractmethod
    def boot(self):
        pass


def get_driver(name):
    """Get driver class.

    :param str name: Driver name.
    :rtype: :py:function:`driver.AbstractDriver`
    """
    return class_for_name(CFG[name].driver)