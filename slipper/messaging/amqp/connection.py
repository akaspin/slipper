# coding=utf-8

from weakref import ref
from kombu import connections, Connection

from slipper.env import CFG
from slipper.utils.decorators import cached_property
from slipper.utils.platforms import detect_environment


class HeartbeatMixin(object):
    """Mixin for heartbeat."""

    @staticmethod
    def spawn_gevent_heartbeat(conn_ref, rate, interval):
        from gevent import spawn_later, spawn
        from amqp.exceptions import ConnectionError

        def heartbeat_check():
            conn = conn_ref()
            if conn is not None and conn.connected:
                try:
                    conn.heartbeat_check(rate=rate)
                except ConnectionError:
                    pass
                spawn_later(interval, heartbeat_check)

        spawn(heartbeat_check)

    def create_heartbeat(self, conn):
        rate = CFG.messaging.heartbeat
        if not conn.heartbeat or not conn.supports_heartbeats:
            return
        interval = conn.heartbeat / float(rate)
        if not conn.connected:
            conn.connect()
        if detect_environment() == 'gevent':
            # amqp with gevent don't support heartbeat, emulate it!
            self.spawn_gevent_heartbeat(ref(conn), rate, interval)


class ConnectibleMixin(object):
    """Connectible class"""

    def __init__(self):
        self._connection = None

    @property
    def connections(self):
        return connections[Connection(
            CFG.messaging.url, heartbeat=CFG.messaging.heartbeat)]

    @cached_property
    def connection(self):
        self._connection = self.connections.acquire(block=True)
        assert self._connection is not None
        return self._connection

    @connection.deleter
    def connection(self):
        if self._connection is not None:
            self._connection.release()
