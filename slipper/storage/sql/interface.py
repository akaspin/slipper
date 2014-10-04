# coding=utf-8
from __future__ import absolute_import

from sqlalchemy.exc import IntegrityError

from ..interface import AbstractStorageAdapter
from slipper.storage.sql.transaction import with_transaction
from slipper.storage.sql.boot import Boot
from .model import Contract, Point
from ..exc import NotUniqueError


class MySQLAdapter(AbstractStorageAdapter):

    __BOOT__ = Boot


    @classmethod
    @with_transaction()
    def create_base_contract(cls, contract, session=None):
        # Store contract
        Contract(uid=contract.uid,
                 timeout=contract.timeout).store(session=session)
        # for point in contract.points:
        #     Point(uid=point.uid,
        #           state=point.state,
        #           dt_activity=point.dt_activity,
        #           dt_finish=point.dt_finish).store(session=session)
        #     Binding(contract_uid=contract.uid,
        #             point_uid=point.uid).store(session=session)
        # try:
        #     # Store internal metadata.
        #     Meta(contract_uid=contract.uid,
        #          is_greedy=True,
        #          routing_key=None,
        #          payload=contract.payload,
        #          metadata_hash=contract.sub_hash).store(session=session)
        # except IntegrityError:
        #     pass
        # try:
        #     Meta(contract_uid=contract.uid,
        #          is_greedy=contract.is_greedy,
        #          routing_key=contract.routing,
        #          payload=contract.payload,
        #          metadata_hash=contract.sub_hash).store(session=session)
        # except IntegrityError:
        #     raise NotUniqueError(entity=Meta, uid=contract.uid)

    @classmethod
    @with_transaction()
    def update_point(cls, point, session=None):

        super(MySQLAdapter, cls).update_point(point)

    @classmethod
    def delete_contract(cls, uid, meta_hash=None):
        super(MySQLAdapter, cls).delete_contract(uid, meta_hash)

    @classmethod
    def get_contract(cls, uid):
        return super(MySQLAdapter, cls).get_contract(uid)

