# coding=utf-8
from abc import ABCMeta, abstractmethod

from six import with_metaclass

from slipper.env import getLogger
from slipper.model.primitives import Contract, Point
from slipper.model import exc as model_exc
from slipper.messaging.interface import interface as messaging
from slipper.storage.interface import interface as storage


CONTRACTS_NEW = 'contracts_new'
INTERNAL = 'internal'
POINTS_NEW = 'points_new'

LOG = getLogger(__name__)


class AbstractHandler(with_metaclass(ABCMeta)):
    """Abstract messaging handler"""
    __SOURCE__ = None

    def __init__(self):
        self.process_uuid = messaging.process_uuid

    @abstractmethod
    def accept(self, data, raw):
        """Accept and process data.

        :param data: Data.
        :type data: str or dict
        :param bool raw: Is message parsed successfully.
        :returns: ``False`` if message processed or ``True`` if message
            needs be processed later.
        :rtype: bool
        """


class ContractsNewHanler(AbstractHandler):
    __SOURCE__ = CONTRACTS_NEW

    def accept(self, data, raw):
        if raw:
            raise model_exc.InvalidContractDataError(data=data)
        contract = Contract.from_serialized(data)
        if contract.routing is None:
            raise model_exc.NotRoutedContractError(data=data)
        storage.adapter.create_contract(contract)
        messaging.adapter.get_producer(INTERNAL).publish(contract.uid)
        LOG.debug('Contract added: %s', data)


class PointsNewHandler(AbstractHandler):
    __SOURCE__ = 'points_new'

    def accept(self, data, raw):
        print self, data


class InternalHandler(AbstractHandler):
    __SOURCE__ = 'internal'

    def accept(self, data, raw):
        print self, data
