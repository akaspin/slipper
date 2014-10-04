# coding=utf-8

from abc import ABCMeta, abstractmethod

from six import with_metaclass


from slipper.interface import AbstractInterface


class AbstractStorageAdapter(with_metaclass(ABCMeta)):
    """Abstract storage interface."""

    @classmethod
    @abstractmethod
    def create_base_contract(cls, contract):
        """Create base contract from ordinal.

        :param contract: Parsed contract.
        :type contract: :py:class:`slipper.model.primitives.Contract`
        :raises NotUniqueError: If contract already exists.
        """

    @classmethod
    @abstractmethod
    def create_sub_contract(cls, contract):
        """Create sub contract.

        :param contract: Parsed contract.
        :type contract: :class:`slipper.model.primitives.Contract`
        :raises NotUniqueError: If contract already exists.
        """

    @classmethod
    @abstractmethod
    def get_contract(cls, uid):
        """Get contract from storage.

        :param str uid: Contract UID.
        :rtype: :py:class:`slipper.model.primitives.Contract`
        """

    @classmethod
    @abstractmethod
    def delete_contract(cls, uid, meta_hash=None):
        """Delete existing contract."""

    @classmethod
    @abstractmethod
    def update_point(cls, point):
        """Update existing interest.

        :param point: Parsed point.
        :type point: :class:`slipper.model.primitives.Point`
        :raises NotFoundError: If interest not found.
        """


class StorageInterface(AbstractInterface):
    __NAME__ = 'storage'


interface = StorageInterface()
