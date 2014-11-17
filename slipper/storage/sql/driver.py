# coding=utf-8

from sqlalchemy.sql.expression import exists, select
from sqlalchemy.orm.exc import NoResultFound

from slipper.model import primitives
from slipper.storage.driver import AbstractStorageDriver
from slipper.storage.exc import NotFoundError
from slipper.storage.sql.transaction import with_transaction, engine
from slipper.storage.sql.schema import Contract, Point, Link, Base


class MySQLDriver(AbstractStorageDriver):

    def boot(self):
        super(MySQLDriver, self).boot()
        Base.metadata.create_all(engine)

    def cleanup(self):
        Base.metadata.drop_all(engine)


    @classmethod
    @with_transaction()
    def create_contract(cls, contract, session=None):
        """Create contract from ordinal.

        :param contract: Parsed contract.
        :type contract: :py:class:`slipper.model.primitives.Contract`
        :raises NotUniqueError: If contract already exists.
        """
        Point.create(contract.points, session=session)
        Contract.create(contract, session=session)
        Link.create(contract, session=session)

    @classmethod
    @with_transaction()
    def get_contract(cls, uid, session=None):
        try:
            res = (session.query(Contract)
                   .filter(Contract.uid == uid)
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
            raise NotFoundError(entity=Contract, uid=uid)

    @classmethod
    @with_transaction()
    def delete_contract(cls, uid, session=None):
        sql = '''
          DELETE points.*, contracts.* FROM points
            JOIN contract_point_links as l ON points.uid = l.point_uid
            LEFT OUTER JOIN contracts ON contracts.uid = l.contract_uid
            WHERE
              l.contract_uid = UNHEX(:contract_uid)
              AND EXISTS (
                SELECT 1 FROM contract_point_links as l
                  WHERE l.point_uid = points.uid
                  GROUP BY l.point_uid
                  HAVING COUNT(l.point_uid) = 1);
        '''
        session.execute(sql, {'contract_uid': uid})

    @classmethod
    @with_transaction()
    def update_point(cls, point, session=None):
        # Update only incomplete points. Exclude NULL values
        # from update data.
        res = session.query(Point).filter(
            Point.uid == point.uid, Point.state.is_(None)).update(
                {k: v for (k, v)
                 in dict(state=point.state,
                         worker=point.worker,
                         dt_activity=point.dt_activity,
                         dt_finish=point.dt_finish).items()
                 if v is not None})
        if res == 0:
            raise NotFoundError(entity=Contract, uid=point.uid)
