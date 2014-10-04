# coding=utf-8
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod, abstractproperty
from binascii import hexlify
from datetime import datetime

from six import with_metaclass

from .identity import compute_hash
from slipper.utils.decorators import cached_property
from slipper.model.exc import InvalidContractDataError, InvalidPointData


class Serializable(with_metaclass(ABCMeta)):

    @classmethod
    @abstractmethod
    def from_serialized(cls, data):
        """Create new instance from setialized form.

        :param dict data: Raw data.
        """

    @abstractproperty
    def serialized(self):
        """Serialize.

        :rtype: dict
        """
        raise NotImplementedError('Child responsibility')


class Point(Serializable):
    """Contract point."""

    def __init__(self, uid, state=None, worker=None,
                 dt_activity=None, dt_finish=None, meta=None):
        """
        :param str uid: Point UID.
        :param int state: (optional) Point state. ``None`` means none
            (surprise!). Zero state means success. Any other is error code.
        :param datetime dt_activity: (optional) Last activity datetime.
        :param datetime dt_finish: (optional) Finish datetime.
        :param dict meta: (optional) Metadata.
        """
        super(Point, self).__init__()
        self.uid = uid
        self.state = state
        self.worker = worker
        self.meta = meta
        self.dt_activity = dt_activity
        self.dt_finish = dt_finish
        if state is None:
            self.dt_activity = dt_activity or datetime.utcnow()
        else:
            self.dt_finish = dt_finish or datetime.utcnow()

    @classmethod
    def from_serialized(cls, data):
        return cls(
            data['uid'],
            state=data.get('state'),
            worker=data.get('worker'),
            meta=data.get('meta'),
            dt_activity=cls.from_timestamp(data.get('dt_activity')),
            dt_finish=cls.from_timestamp(data.get('dt_finish'))
        )

    @property
    def serialized(self):
        return dict(uid=self.uid,
                    state=self.state,
                    worker=self.worker,
                    dt_activity=self.to_timestamp(self.dt_activity),
                    dt_finish=self.to_timestamp(self.dt_finish),
                    meta=self.meta)

    @staticmethod
    def to_timestamp(dt, epoch=datetime(1970,1,1)):
        if dt is not None:
            td = dt - epoch
            return td.total_seconds()

    @staticmethod
    def from_timestamp(ts):
        if ts is not None:
            return datetime.utcfromtimestamp(ts)


class Contract(Serializable):
    """Contract. """

    def __init__(self, points=None, timeout=None, routing=None,
                 is_greedy=True, payload=None):
        """
        :param points: Contract points.
        :param int timeout: Expiration date.
        :param str routing: Report routing key. Used for route contract
            report.
        :param bool is_greedy: (optional) Greedy behaviour.
        :param str payload: (optional) Payload
        :type points: list[Point]
        """
        self.points = points
        self.timeout = timeout
        self.is_greedy = is_greedy
        self.routing = routing
        self.payload = payload
        if not points or not timeout:
            raise InvalidContractDataError(data=self.serialized)

    @property
    def is_base(self):
        """Is contract base."""
        return self.routing is None and self.payload is None and self.is_greedy

    @property
    def base(self):
        """Get base contract."""
        return Contract(
            
        )

    @property
    def uid(self):
        return compute_hash(*sorted([point.uid for point in self.points]))

    @property
    def sub_hash(self):
        return compute_hash(self.is_greedy, self.timeout, self.payload)

    @classmethod
    def from_serialized(cls, data):
        return cls(
            points=[Point(raw) for raw in data.get('points', [])],
            timeout=data.get('timeout'),
            is_greedy=data.get('is_greedy', True),
            routing=data.get('routing'),
            payload=data.get('payload')
        )

    @property
    def serialized(self):
        """Serialize contract report.

        :rtype: dict
        """

        return Point(
            uid=self.uid,
            state=all(point.state == 0 for point in self.points),

            meta=dict(

            )
        )

