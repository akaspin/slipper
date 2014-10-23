# coding=utf-8

from abc import ABCMeta, abstractmethod

from six import with_metaclass

from slipper.utils.proxy import PromiseProxy
from slipper.driver import AbstractDriver, get_driver


class AbstractStorageDriver(AbstractDriver):

    @classmethod
    @abstractmethod
    def create_contract(cls, contract):
        """Create contract in storage.

        :param contract: Parsed contract.
        :type contract: :py:class:`slipper.model.primitives.Contract`
        :raises NotUniqueError: If contract already exists.
        """

    @classmethod
    @abstractmethod
    def get_contract(cls, uid, sub_hash):
        """Get contract from storage.

        :param str uid: Contract UID.
        :param str sub_hash: Subcontract HASH.
        :rtype: :py:class:`slipper.model.primitives.Contract`
        :raises :py:class:`slipper.storage.exc.NotFoundError`:
            When contract not found.
        """

    @classmethod
    @abstractmethod
    def delete_contract(cls, uid, sub_hash):
        """Delete existing contract.

        :param str uid: Contract UID.
        :param str sub_hash: Subcontract HASH.
        :raises :py:class:`slipper.storage.exc.NotFoundError`:
            When contract not found.
        """

    @classmethod
    @abstractmethod
    def update_point(cls, point):
        """Update existing point.

        :param point: Parsed point.
        :type point: :class:`slipper.model.primitives.Point`
        :raises :py:class:`slipper.storage.exc.NotFoundError`:
            When point not found.
        """


#: Storage driver
DRIVER = PromiseProxy(lambda: get_driver('storage')())
""":type : :py:class:`slipper.storage.interface.AbstractStorageDriver`"""