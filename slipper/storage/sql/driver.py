# coding=utf-8

from sqlalchemy.orm.exc import NoResultFound

from slipper.model import primitives
from slipper.storage.driver import AbstractStorageDriver
from slipper.storage.exc import NotFoundError
from slipper.storage.sql.transaction import with_transaction, engine
from slipper.storage.sql.schema import Contract, Point, Base


class MySQLDriver(AbstractStorageDriver):

    def boot(self):
        super(MySQLDriver, self).boot()
        Base.metadata.create_all(engine)

    @classmethod
    @with_transaction()
    def create_contract(cls, contract, session=None):
        """Create contract from ordinal.

        :param contract: Parsed contract.
        :type contract: :py:class:`slipper.model.primitives.Contract`
        :raises NotUniqueError: If contract already exists.
        """
        points = Point.make_points(contract.points, session=session)
        c = Contract(uid=contract.uid,
                     timeout=contract.timeout,
                     strict=contract.strict,
                     route=contract.route,
                     payload=contract.payload)
        session.add(c)
        c.points = points
        session.flush()

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
        res = session.query(Contract).filter(
            Contract.uid == uid).one()
        session.delete(res)
        for point in res.points:
            if len(point.contracts) == 1 and point.contracts[0] == res:
                session.delete(point)

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
