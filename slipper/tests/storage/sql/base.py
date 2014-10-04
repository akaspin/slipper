# coding=utf-8

import unittest

from slipper.storage.interface import interface
from slipper.storage.sql.schema import Base


class DBTestBase(unittest.TestCase, object):

    def setUp(self):
        Base.metadata.drop_all(interface.boot.engine)
        Base.metadata.create_all(interface.boot.engine)
        super(DBTestBase, self).setUp()
