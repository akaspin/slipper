# coding=utf-8
from __future__ import absolute_import

from sqlalchemy.orm.exc import NoResultFound

from slipper.model import primitives
from slipper.storage.interface import AbstractStorageAdapter
from slipper.storage.exc import NotUniqueError, NotFoundError
from slipper.storage.sql.transaction import with_transaction
from slipper.storage.sql.boot import Boot
from slipper.storage.sql.schema import Contract, Point


class MySQLAdapter(AbstractStorageAdapter):

    __BOOT__ = Boot

    @classmethod
    @with_transaction()
    def create_contract(cls, contract, session=None):
        """Create contract from ordinal.

        :param contract: Parsed contract.
        :type contract: :py:class:`slipper.model.primitives.Contract`
        :raises NotUniqueError: If contract already exists.
        """
        base_res = cls._create(contract.base, session=session)
        sub_res = None
        if not contract.is_base:
            sub_res = cls._create(contract, session=session)
        return base_res, sub_res

    @classmethod
    @with_transaction()
    def _create(cls, contract, session=None):
        try:
            Contract(
                uid=contract.uid,
                timeout=contract.timeout,
                sub_hash=contract.sub_hash,
                strict=contract.strict,
                route=contract.route,
                payload=contract.payload,
                points=[Point(
                    uid=p.uid,
                    contract_uid=contract.uid,
                    state=p.state,
                    worker=p.worker,
                    dt_activity=p.dt_activity,
                    dt_finish=p.dt_finish,
                    payload=p.payload
                ) for p in contract.points]
            ).store(session=session)
            return contract
        except NotUniqueError:
            pass

    @classmethod
    @with_transaction()
    def get_contract(cls, uid, sub_hash, session=None):
        try:
            res = (session.query(Contract)
                   .filter(Contract.uid == uid, Contract.sub_hash == sub_hash)
                   .one())
            return primitives.Contract(
                points=[primitives.Point(
                    uid=p.uid,
                    state=p.state,
                    worker=None,
                    dt_activity=p.dt_activity,
                    dt_finish=p.dt_finish,
                    payload=p.payload
                ) for p in res.points],
                timeout=res.timeout,
                route=res.route,
                strict=res.strict,
                payload=res.payload
            )
        except NoResultFound:
            raise NotFoundError(entity=Contract, uid='-'.join([uid, sub_hash]))

    @classmethod
    @with_transaction()
    def delete_contract(cls, uid, sub_hash, session=None):
        session.query(Contract).filter(Contract.uid == uid,
                                       Contract.sub_hash == sub_hash).delete()

    @classmethod
    @with_transaction()
    def update_point(cls, point, session=None):
        # Update only incomplete points. Exclude NULL values
        # from update data.
        values = dict(
            state=point.state,
            worker=point.worker,
            dt_activity=point.dt_activity,
            dt_finish=point.dt_finish
        )
        return session.query(Point).filter(
            Point.uid == point.uid, Point.state.is_(None)).update(
                {k: v for (k, v) in values.items() if v is not None})
