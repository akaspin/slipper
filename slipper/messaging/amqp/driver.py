# coding=utf-8

from kombu import Exchange, Queue

from slipper.env import CFG
from slipper.utils.proxy import PromiseProxy

from slipper.messaging.driver import AbstractMessagingDriver
from slipper.messaging.amqp.consumer import Consumer
from slipper.messaging.amqp.producer import Producer
from slipper.messaging.amqp.schema import _exchanges


class KombuDriver(AbstractMessagingDriver):

    def __init__(self):
        self._exchanges = {
            'contracts': PromiseProxy(lambda: Exchange(
                'slipper.contracts',
                durable=True,
                type='direct',
                delivery_mode='persistent')),
            'points': PromiseProxy(lambda: Exchange(
                'slipper.points',
                durable=True,
                type='direct',
                delivery_mode='persistent')),
        }

        self._SOURCES = {
            ('contracts', 'new'): Queue(
                'slipper.contracts.new',
                exchange=_exchanges['contracts'],
                routing_key='new'),
            ('contracts', 'schedule'): Queue(
                'slipper.contracts.schedule',
                exchange=_exchanges['contracts'],
                routing_key='schedule'),
            ('points', 'new'): Queue(
                'slipper.points.new',
                exchange=_exchanges['points'],
                routing_key='new'),
            ('points', None): Queue(
                'slipper.points.%s' % CFG.process_uuid,
                auto_delete=True,
                exchange=_exchanges['points'],
                routing_key=CFG.process_uuid),
        }

        self._DESTINATIONS = {
            ('contracts', 'new'): self._get_producer('contracts', 'new'),
            ('contracts', 'schedule'): self._get_producer('contracts',
                                                          'schedule'),
            ('points', 'new'): self._get_producer('points', 'new'),
            ('points', None): self._get_producer('points',
                                                 route=CFG.process_uuid),
        }

    def get_consumer(self, handler):
        queue = self._SOURCES[handler.__SOURCE__]
        return PromiseProxy(lambda: Consumer(handler().accept, queue))

    def get_producer(self, destination):
        return self._DESTINATIONS[destination]

    def _get_producer(self, base, route):
        return PromiseProxy(lambda: Producer(self._exchanges[base],
                                             route=route))


