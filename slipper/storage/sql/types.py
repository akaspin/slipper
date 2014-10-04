# coding=utf-8

from binascii import hexlify, unhexlify
import uuid

import simplejson as json
from simplejson.encoder import JSONEncoder
from sqlalchemy import types
from sqlalchemy.types import TypeDecorator, TEXT, BINARY


class UUID(types.TypeDecorator):
    """BINARY UUID SQLAlchemy type decorator."""
    impl = BINARY
    UID_BINARY_S = 16

    def __init__(self):
        self.impl.length = self.UID_BINARY_S
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, uuid.UUID):
            return unhexlify(value.hex)
        elif value and isinstance(value, basestring):
            return unhexlify(uuid.UUID(hex=value).hex)
        elif value and not isinstance(value, uuid.UUID):
            raise ValueError('value %s is not a valid uuid.UUID' % value)
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value and isinstance(value, basestring):
            return uuid.UUID(hex=hexlify(value))
        else:
            return None


class ExtendedJSONEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, set):
            return list(o)
        else:
            return super(ExtendedJSONEncoder, self).default(o)


class JSON(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, cls=ExtendedJSONEncoder)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class HASH(types.TypeDecorator):
    """BINARY hash SQLAlchemy type decorator"""
    impl = BINARY

    def __init__(self):
        self.impl.length = 20
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, basestring):
            # Assume that value is HEX.
            return unhexlify(value)
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value and isinstance(value, basestring):
            return hexlify(value)
        else:
            return None

