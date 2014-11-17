# coding=utf-8
from __future__ import absolute_import

from sqlalchemy import Column, ForeignKeyConstraint, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Text, DateTime, Boolean, String, Integer

from slipper.storage.exc import NotUniqueError
from slipper.storage.sql.types import SHA1, UUID, JSON
from slipper.storage.sql.transaction import with_transaction


Base = declarative_base()


class Contract(Base):
    """Contract."""

    __tablename__ = 'contracts'

    #: Contract UID
    uid = Column('uid', SHA1, nullable=False, primary_key=True)

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


class Point(Base):
    """Points."""

    __tablename__ = 'points'

    #: Point UID. SHA1 hash.
    uid = Column('uid', SHA1, primary_key=True)

    #: Point state. ``None`` means what interest being processed.
    #: Zero value - OK. Any positive value is error code.
    state = Column('state', Integer, index=True, nullable=True,
                   default=None)

    #: Worker. Used only for native behaviour.
    worker = Column('worker', SHA1, nullable=True, index=True, default=None)

    #: Last activity. In non-native behaviour is contract creation.
    dt_activity = Column('dt_activity', DateTime, nullable=False, index=True)

    #: Finish process datetime.
    dt_finish = Column('dt_finish', DateTime, nullable=True, index=True,
                       default=None)

    payload = Column('payload', JSON, nullable=True)

    @classmethod
    @with_transaction()
    def create(cls, points, session=None):
        """Create points."""
        session.execute(cls.__table__.insert().prefix_with("IGNORE"), [{
            'uid': point.uid,
            'state': point.state,
            'worker': point.worker,
            'dt_activity': point.dt_activity,
            'dt_finish': point.dt_finish,
            'payload': point.payload
        } for point in points])


class Link(Base):
    """Points to contracts bindings."""

    __tablename__ = 'contract_point_links'

    contract_uid = Column('contract_uid', SHA1,
                          ForeignKey(Contract.uid, ondelete='CASCADE'),
                          primary_key=True)
    point_uid = Column('point_uid', SHA1,
                       ForeignKey(Point.uid, ondelete='CASCADE'),
                       primary_key=True)

    @classmethod
    @with_transaction()
    def create(cls, contract, session=None):
        session.execute(cls.__table__.insert(), [{
            'contract_uid': contract.uid,
            'point_uid': point.uid
        } for point in contract.points])
