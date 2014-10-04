# coding=utf-8

from contextlib import contextmanager

from kombu.mixins import ConsumerMixin
import msgpack

from slipper import env
from slipper.messaging.amqp.connection import HeartbeatMixin, ConnectibleMixin


LOG = env.getLogger(__name__)


class Consumer(ConnectibleMixin, HeartbeatMixin, ConsumerMixin):
    """Abstact Consumer."""

    def __init__(self, callback, queue):
        """
        :param callback: Callback handler.
        """
        self.callback = callback
        self.queue = queue
        super(Consumer, self).__init__()

    @contextmanager
    def extra_context(self, connection, channel):
        """Context. Used for heartbeat.

        :param connection: Connection
        :param channel: Channel.
        """
        self.create_heartbeat(connection)
        yield

    def on_consume_end(self, connection, default_channel):
        """Consume end hook.

        :param connection: Connection
        :param default_channel: Channel.
        """
        del self.connection

    def process(self, body, message):
        """Message handler.

        :param body: Message body.
        :param message: Message.
        :type message: :py:class:`kombu.message.Message`
        """
        try:
            body, raw = self.parse(body)
            if not self.callback(body, raw):
                message.ack()
            else:
                message.requeue()
        except Exception as e:
            message.ack()
            LOG.error('Message not handled: %s', e)

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[self.queue], callbacks=[self.process])]

    @staticmethod
    def parse(body):
        """Parse message body."""
        try:
            return msgpack.unpackb(body), False
        except msgpack.ExtraData:
            return body, True
