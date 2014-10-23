# coding=utf-8

from abc import ABCMeta

from six import with_metaclass

from slipper.utils.imports import class_for_name
from slipper.utils.decorators import cached_property
from slipper.env import CFG


class AbstractInterface(with_metaclass(ABCMeta)):
    #: Interface name
    __NAME__ = None

    @cached_property
    def adapter(self):
        """Interface adapter."""
        return class_for_name(self.__props.adapter)()

    @cached_property
    def __props(self):
        return CFG[self.__NAME__]
