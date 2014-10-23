# coding=utf-8

from slipper.tests.base import BaseTestCase

from slipper.storage.sql.transaction import engine
from slipper.storage.sql.schema import Base


class DBTestBase(BaseTestCase):

    def setUp(self):
        super(DBTestBase, self).setUp()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
