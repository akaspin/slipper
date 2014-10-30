# coding=utf-8
from abc import ABCMeta, abstractmethod
from logging import getLogger

from six import with_metaclass

from slipper.env import CFG
from slipper.utils.decorators import cached_property

from slipper.model.identity import compute_hash
from slipper.model.primitives import Contract, Point
from slipper.model import exc as model_exc
from slipper.messaging.driver import DRIVER as MESSAGING
from slipper.storage.driver import DRIVER as STORAGE


LOG = getLogger(__name__)


class AbstractHandler(with_metaclass(ABCMeta)):
    """Abstract messaging handler"""
    __SOURCE__ = None

    def __init__(self):
        self.process_uuid = CFG.process_uuid

    @abstractmethod
    def accept(self, data, raw):
        """Accept and process data.

        :param data: Data.
        :type data: str or dict
        :param bool raw: Non parsed message.
        :returns: ``False`` if message processed or ``True`` if message
            needs be processed later.
        :rtype: bool
        """


class ContractsNewHanler(AbstractHandler):
    """Handler to register new contract."""

    __SOURCE__ = ('contracts', 'new')

    def accept(self, data, raw):
        if raw:
            raise model_exc.InvalidContractDataError(data=data)
        contract = Contract.from_serialized(data)
        STORAGE.create_contract(contract)
        self._schedule_producer.publish(contract.uid)
        LOG.debug('Contract added: %s', data)

    @cached_property
    def _schedule_producer(self):
        return MESSAGING.get_producer(('contracts', 'schedule'))


class PointsNewHandler(AbstractHandler):
    """Handler to accept points notifications."""

    __SOURCE__ = ('points', 'new')

    def accept(self, data, raw):
        point = Point(uid=compute_hash(data)) if raw else \
            Point.from_serialized(data)
        STORAGE.update_point(point)


class ScheduleHandler(AbstractHandler):
    __SOURCE__ = ('contracts', 'schedule')

    def accept(self, data, raw):
        print self, data


class WaiterHandler(AbstractHandler):
    __SOURCE__ = ('points', None)

    def accept(self, data, raw):
        print self, data
