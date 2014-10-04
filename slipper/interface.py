# coding=utf-8

from abc import ABCMeta, abstractmethod, abstractproperty

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
    def process_uuid(self):
        """Process UUID"""
        return CFG.process_uuid

    @cached_property
    def boot(self):
        """Boot from adapter."""
        if self.adapter.__BOOT__ is not None:
            props = dict(self.__props)
            props.pop('adapter')
            return self.adapter.__BOOT__(**props)

    @cached_property
    def __props(self):
        return CFG[self.__NAME__][
            CFG[self.__NAME__].use]
