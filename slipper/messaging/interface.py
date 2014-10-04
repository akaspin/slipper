# coding=utf-8

from abc import ABCMeta, abstractmethod

from six import with_metaclass

from slipper.interface import AbstractInterface


class AbstractMessagingAdapter(with_metaclass(ABCMeta)):
    """Messaging adapter."""

    @abstractmethod
    def get_consumer(self, handler):
        """Get consumer for source.

        :param handler: Handler.
        :type handler: :py:class:`slipper.messaging.handler.AbstractHandler`
        :rtype: () -> None
        """
        raise NotImplementedError('Child responsibility.')

    @abstractmethod
    def get_producer(self, destination):
        """Get producer"""


class MessagingInterface(AbstractInterface):
    __NAME__ = 'messaging'


interface = MessagingInterface()
