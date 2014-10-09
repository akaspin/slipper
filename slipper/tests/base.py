# coding=utf-8

import unittest
import logging

# from slipper.storage.interface import StorageInterface
from slipper.storage.interface import interface
from slipper.storage.sql.model import Base


class DBTestBase(unittest.TestCase, object):

    def setUp(self):
        Base.metadata.drop_all(interface.boot.engine)
        Base.metadata.create_all(interface.boot.engine)
        super(DBTestBase, self).setUp()
