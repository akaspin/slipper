# coding=utf-8
from kombu.pools import ProducerPool
import msgpack

from slipper.messaging.amqp.connection import ConnectibleMixin


class Producer(ConnectibleMixin):
    """Produce and publish messages"""

    def __init__(self, exchange, route=None):
        self.producers = ProducerPool(self.connections)
        self.exchange = exchange
        self.route = route or ''
        super(Producer, self).__init__()

    def publish(self, body, route=None):
        """Publish message.

        :param body: Message body.
        :param route: Message route.
        :type route: str or None
        """
        with self.producers.acquire(block=True) as producer:
            producer.publish(msgpack.packb(body, use_bin_type=True),
                             exchange=self.exchange,
                             routing_key=route or self.route)

