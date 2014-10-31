# coding=utf-8
from __future__ import absolute_import

import uuid
from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime, timedelta
from operator import attrgetter

from six import with_metaclass

from slipper.model.exc import InvalidContractDataError, InvalidPointData


class Serializable(with_metaclass(ABCMeta)):

    def __init__(self, uid=None):
        self.uid = uid or uuid.uuid4()

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

    def __init__(self, uid=None, state=None, worker=None,
                 dt_activity=None, dt_finish=None, payload=None):
        """
        :param uid: Point UID.
        :type uid: :py:class:`uuid.UUID`
        :param int state: (optional) Point state. ``None`` means none
            (surprise!). Zero state means success. Any other is error code.
        :param datetime dt_activity: (optional) Last activity datetime.
        :param datetime dt_finish: (optional) Finish datetime.
        :param dict payload: (optional) Metadata.
        """
        super(Point, self).__init__(uid)
        self.uid = uid or uuid.uuid4()
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
            uuid.UUID(data['uid']),
            state=data.get('state'),
            worker=data.get('worker'),
            payload=data.get('payload'),
            dt_activity=cls.from_timestamp(data.get('dt_activity')),
            dt_finish=cls.from_timestamp(data.get('dt_finish'))
        )

    @property
    def serialized(self):
        return dict(uid=str(self.uid),
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
    """Contracts are divided into two types: base and routed.

    Base contracts hasn't route info. They are used as internal dependencies.
    Base contract are always non-strict and hasn't payload.
    """

    #: Normal state
    OK = 0

    #: Dependencies failed
    FAILED = 1

    def __init__(self, points, timeout, uid=None, route=None,
                 strict=False, payload=None):
        """
        :param uid: Contract ID.
        :type uid: :py:class:`uuid.UUID`
        :param points: Contract points.
        :type points: list[:py:class:`slipper.model.primitives.Point`]
        :param int timeout: Last activity timeout.
        :param str route: (optional) Report routing key. Used for route
            contract report. Default is ``None``
        :param bool strict: (optional) Strict behaviour. Strict contracts
            fail on first failed point. Default is ``False``
        :param str payload: (optional) Payload.
        """
        super(Contract, self).__init__(uid)
        self.points = sorted(points, key=attrgetter('uid'))
        self.timeout = timeout
        self.strict = strict
        self.route = route
        self.payload = payload
        # Check base contract
        if route is None and strict:
            raise InvalidContractDataError(data=self.serialized)

    @property
    def state(self):
        """Contract state.

        :returns: Contract state based contract props and points states.
            ``None`` means what contract is incomplete. Zero (``0``) means
            what contract is ready. Also state may become error code.
        :rtype: int or None
        """
        res = []
        for point in self.points:
            state = point.get_state(self.timeout)
            res.append(state)
            if not self.strict and state is None:
                # Non-strict contracts must wait for all states.
                return None
            if self.strict and state is not None and state != 0:
                # Strict contracts fail on first error.
                return self.FAILED
        if None not in res:
            return self.FAILED if any(s != 0 for s in res) else self.OK

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
            state=self.state,
            payload={'points': [p.serialized for p in self.points],
                     'payload': self.payload}
        ).serialized

