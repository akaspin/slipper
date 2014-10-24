# coding=utf-8

from slipper.utils.proxy import PromiseProxy

from slipper.messaging.driver import AbstractMessagingDriver
from slipper.messaging.amqp.consumer import Consumer
from slipper.messaging.amqp.producer import Producer
from slipper.messaging.amqp.schema import exchanges, queues






class KombuDriver(AbstractMessagingDriver):

    def boot(self):
        pass

    def get_consumer(self, handler):
        queue = queues[handler.__SOURCE__]
        return PromiseProxy(lambda: Consumer(handler().accept, queue))

    def get_producer(self, destination):
        return PromiseProxy(lambda: Producer(exchanges[destination]))


