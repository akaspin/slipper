# coding=utf-8
from __future__ import absolute_import

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Text, DateTime, Boolean, SmallInteger, String, \
    Integer

from .types import HASH
from ...model.identity import compute_hash
from .transaction import with_transaction


Base = declarative_base()


class StorableMixin(object):
    """StorableMixin model."""

    def __init__(self, **kwargs):
        super(StorableMixin, self).__init__()

    @with_transaction(no_raise=[IntegrityError])
    def store(self, session=None):
        session.add(self)
        session.flush()


class Contract(Base, StorableMixin):
    """Contract."""

    __tablename__ = 'contracts'

    #: Contract UID
    uid = Column('uid', HASH, nullable=False, unique=False,
                 primary_key=True)

    #: Last activity timeout.
    timeout = Column('timeout', Integer, nullable=False, index=True)

    #: Metadata hash from `is_greedy`, `route` and `payload`.
    metadata_hash = Column('metadata_hash', HASH, nullable=False,
                           unique=False, primary_key=True)

    #: Behaviour.
    is_greedy = Column('is_greedy', Boolean, nullable=False, default=True)

    #: Report routing key.
    route = Column('route', String(255), nullable=True)

    #: Report payload.
    payload = Column('payload', Text, nullable=True)

    #: Bindings relationship.
    bindings = relationship('Binding', lazy='joined', backref='contract')

    @with_transaction()
    def is_exists(self, session=None):
        return (session.query(Contract.uid)
                .filter(Contract.uid == self.uid).first()) is not None


class Point(Base, StorableMixin):
    """Points."""

    __tablename__ = 'points'

    #: Point UID. SHA1 hash.
    uid = Column('uid', HASH, primary_key=True)

    #: Contract UID.
    contract_uid = Column('contract_uid', HASH,
                          ForeignKey(Contract.uid, ondelete='CASCADE'),
                          nullable=False, unique=False,
                          primary_key=True)

    #: Point state. ``None`` means what interest being processed.
    #: Zero value - OK. Any positive value is error code.
    state = Column('state', SmallInteger, index=True, nullable=True,
                   default=None)

    #: Worker. Used only for native behaviour.
    worker = Column('worker', HASH, nullable=True, index=True, default=None)

    #: Last activity. In non-native behaviour is contract creation.
    dt_activity = Column('dt_activity', DateTime, nullable=False, index=True)

    #: Finish process datetime.
    dt_finish = Column('dt_finish', DateTime, nullable=True, index=True,
                       default=None)

    @with_transaction()
    def is_exists(self, session=None):
        return (session.query(Point.uid)
                .filter(Point.uid == self.uid).first()) is not None

    @with_transaction()
    def report(self):
        """Update point info"""


