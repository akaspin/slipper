# coding=utf-8

from abc import abstractmethod

from slipper.utils.proxy import PromiseProxy
from slipper.driver import AbstractDriver, get_driver


class AbstractStorageDriver(AbstractDriver):

    @classmethod
    @abstractmethod
    def create_contract(cls, contract):
        """Create contract and points in storage.



        :param contract: Parsed contract.
        :type contract: :py:class:`slipper.model.primitives.Contract`
        :raises NotUniqueError: If contract already exists.
        """

    @classmethod
    @abstractmethod
    def get_contract(cls, uid):
        """Get contract with points from storage.

        :param str uid: Contract UID.
        :rtype: :py:class:`slipper.model.primitives.Contract`
        :raises :py:class:`slipper.storage.exc.NotFoundError`:
            When contract not found.
        """

    @classmethod
    @abstractmethod
    def delete_contract(cls, uid):
        """Delete existing contract and points from storage.

        :param str uid: Contract UID.
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