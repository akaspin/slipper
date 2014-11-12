# coding=utf-8
from __future__ import absolute_import

from sqlalchemy import Column, ForeignKeyConstraint, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Text, DateTime, Boolean, String, Integer

from slipper.storage.exc import NotUniqueError
from slipper.storage.sql.types import HASH, UUID, JSON
from slipper.storage.sql.transaction import with_transaction


Base = declarative_base()


class StorableMixin(object):
    """StorableMixin model."""

    def __init__(self, **kwargs):
        super(StorableMixin, self).__init__()

    @with_transaction()
    def store(self, session=None):
        """Store object.

        :raises NotUniqueError: If object already exists.
        """
        try:
            session.add(self)
            session.flush()
        except IntegrityError:
            raise NotUniqueError(entity=self, uid=self.uid)


class Contract(Base, StorableMixin):
    """Contract."""

    __tablename__ = 'contracts'

    #: Contract UID
    uid = Column('uid', UUID, nullable=False, unique=False,
                 primary_key=True)

    #: Last activity timeout.
    timeout = Column('timeout', Integer, nullable=False, index=True)

    #: Behaviour.
    strict = Column('strict', Boolean, nullable=False, default=False)

    #: Report routing key.
    route = Column('route', String(255), nullable=True)

    #: Report payload.
    payload = Column('payload', Text, nullable=True)

    #: Bindings relationship.
    points = relationship('slipper.storage.sql.schema.Point',
                          secondary='contract_point_links',
                          lazy='joined',
                          backref=backref('contracts',))

    @classmethod
    @with_transaction()
    def create(cls, contract, session=None):
        session.execute(cls.__table__.insert(), [{
            'uid': contract.uid,
            'timeout': contract.timeout,
            'strict': contract.strict,
            'route': contract.route,
            'payload': contract.payload
        }])


class Point(Base, StorableMixin):
    """Points."""

    __tablename__ = 'points'

    #: Point UID. SHA1 hash.
    uid = Column('uid', UUID, primary_key=True)

    #: Point state. ``None`` means what interest being processed.
    #: Zero value - OK. Any positive value is error code.
    state = Column('state', Integer, index=True, nullable=True,
                   default=None)

    #: Worker. Used only for native behaviour.
    worker = Column('worker', HASH, nullable=True, index=True, default=None)

    #: Last activity. In non-native behaviour is contract creation.
    dt_activity = Column('dt_activity', DateTime, nullable=False, index=True)

    #: Finish process datetime.
    dt_finish = Column('dt_finish', DateTime, nullable=True, index=True,
                       default=None)

    payload = Column('payload', JSON, nullable=True)

    @classmethod
    @with_transaction()
    def get_by_uids(cls, uids, session=None):
        """Get points by UIDs."""
        return session.query(cls).filter(cls.uid.in_(uids)).all()

    @classmethod
    @with_transaction()
    def create(cls, points, session=None):
        """Create points."""
        session.execute(cls.__table__.insert().prefix_with("IGNORE"), [{
            'uid': point.uid.hex,
            'state': point.state,
            'worker': point.worker,
            'dt_activity': point.dt_activity,
            'dt_finish': point.dt_finish,
            'payload': point.payload
        } for point in points])


class Link(Base, StorableMixin):
    """Points to contracts bindings."""

    __tablename__ = 'contract_point_links'

    contract_uid = Column('contract_uid', UUID,
                          ForeignKey(Contract.uid, ondelete='CASCADE'),
                          primary_key=True)
    point_uid = Column('point_uid', UUID,
                       ForeignKey(Point.uid, ondelete='RESTRICT'),
                       primary_key=True)

    @classmethod
    @with_transaction()
    def create(cls, contract, session=None):
        session.execute(cls.__table__.insert(), [{
            'contract_uid': contract.uid,
            'point_uid': point.uid
        } for point in contract.points])
