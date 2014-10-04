# coding=utf-8
from kombu.pools import ProducerPool
import msgpack

from slipper.messaging.amqp.connection import ConnectibleMixin


class Producer(ConnectibleMixin):
    """Produce and publish messages"""

    def __init__(self, exchange):
        self.producers = ProducerPool(self.connections)
        self.exchange = exchange
        super(Producer, self).__init__()

    def publish(self, body, limit=None):
        """Publish message.

        :param body: Message body
        :param limit: Limit
        """
        with self.producers.acquire(block=True) as producer:
            producer.publish(msgpack.packb(body, use_bin_type=True),
                             exchange=self.exchange)

    def __call__(self, body):
        """Shortcut for `publish`.

        :param body: Message body.
        """
        self.publish(body)
