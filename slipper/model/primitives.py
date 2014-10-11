# coding=utf-8
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime, timedelta
from operator import itemgetter, attrgetter

from six import with_metaclass

from .identity import compute_hash
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
                 dt_activity=None, dt_finish=None, payload=None):
        """
        :param str uid: Point UID.
        :param int state: (optional) Point state. ``None`` means none
            (surprise!). Zero state means success. Any other is error code.
        :param datetime dt_activity: (optional) Last activity datetime.
        :param datetime dt_finish: (optional) Finish datetime.
        :param dict payload: (optional) Metadata.
        """
        super(Point, self).__init__()
        self.uid = uid
        self.state = state
        self.worker = worker
        self.payload = payload
        self.dt_activity = dt_activity
        self.dt_finish = dt_finish
        if dt_activity is None and state is None:
            self.dt_activity = dt_activity or datetime.utcnow()
        elif dt_finish is None and state is not None:
            self.dt_finish = dt_finish or datetime.utcnow()

    def get_state(self, timeout):
        """Get point state.

        :param int timeout: Timeout.
        :returns: Integer state, `-1` if point expired, `None`
            if point in progress.
        :rtype: int or None
        """
        if self.state is not None:
            return self.state
        if self.dt_activity + timedelta(seconds=timeout) < datetime.utcnow():
            return -1

    @classmethod
    def from_serialized(cls, data):
        return cls(
            data['uid'],
            state=data.get('state'),
            worker=data.get('worker'),
            payload=data.get('payload'),
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
                    payload=self.payload)

    @staticmethod
    def to_timestamp(dt, epoch=datetime(1970,1,1)):
        if dt is not None:
            td = dt - epoch
            return round(td.total_seconds())

    @staticmethod
    def from_timestamp(ts):
        if ts is not None:
            return datetime.utcfromtimestamp(ts)


class Contract(Serializable):
    """Contract.

    Contracts are divided into two types: base and routed.
    """

    #: Normal state
    OK = 0

    #: Contract expired
    EXPIRED = 1

    #: Dependencies failed
    FAILED = 2

    def __init__(self, points=None, timeout=None, route=None,
                 strict=False, payload=None):
        """
        :param points: Contract points.
        :param int timeout: Expiration date.
        :param str route: Report routing key. Used for route contract
            report.
        :param bool strict: (optional) Greedy behaviour.
        :param str payload: (optional) Payload
        :type points: list[Point]
        """

        self.points = sorted(points, key=attrgetter('uid'))
        self.timeout = timeout
        self.strict = strict
        self.route = route
        self.payload = payload
        # Check conditions
        if not points or not timeout:
            raise InvalidContractDataError(data=self.serialized)
        # Check base contract
        if route is None and (strict or payload is not None):
            raise InvalidContractDataError(data=self.serialized)


    @property
    def is_base(self):
        """Is contract base."""
        return self.route is None and self.payload is None and not self.strict

    @property
    def is_done(self):
        """Is contract done. Regardless of errors."""
        for point in self.points:
            # If contract is strict and point failed - close contract.
            state = point.get_state(self.timeout)
            if self.strict and state is not None and state != 0:
                return True
            if state is None:
                return False
        return True

    @property
    def base(self):
        """Get base contract."""
        if self.is_base:
            return self
        else:
            return Contract(points=self.points, timeout=self.timeout)

    @property
    def uid(self):
        return compute_hash(*(point.uid for point in self.points))

    @property
    def sub_hash(self):
        return compute_hash(self.route, self.strict, self.payload)

    @classmethod
    def from_serialized(cls, data):
        return cls(
            points=[Point.from_serialized(raw)
                    for raw in data.get('points', [])],
            timeout=data.get('timeout'),
            strict=data.get('strict', False),
            route=data.get('route'),
            payload=data.get('payload')
        )

    @property
    def serialized(self):
        return {
            'points': [p.serialized for p in self.points],
            'timeout': self.timeout,
            'strict': self.strict,
            'route': self.route,
            'payload': self.payload
        }

    @property
    def report(self):
        """Serialize contract report. State is always zero.

        :rtype: dict
        """
        return Point(
            uid=self.uid,
            state=0,
            payload={'points': [p.serialized for p in self.points],
                     'payload': self.payload}
        ).serialized

