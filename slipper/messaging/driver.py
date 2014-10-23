# coding=utf-8

from abc import abstractmethod

from slipper.utils.proxy import PromiseProxy

from slipper.driver import AbstractDriver, get_driver


class AbstractMessagingDriver(AbstractDriver):

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


DRIVER = PromiseProxy(lambda: get_driver('messaging')())