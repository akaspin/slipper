# coding=utf-8
from __future__ import absolute_import

from datetime import timedelta, datetime

from slipper.model import primitives
from slipper.model.primitives import compute_hash
from slipper.storage.driver import DRIVER
from slipper.storage import exc

from slipper.tests.storage.sql.base import DBTestBase


class IntersectedTestCase(DBTestBase):

    def setUp(self):
        super(IntersectedTestCase, self).setUp()
        self.points = [primitives.Point(compute_hash(i)) for i in range(6)]
        self.contract1 = primitives.Contract(points=self.points[:3],
                                             timeout=30)
        self.contract2 = primitives.Contract(points=self.points[2:],
                                             timeout=30)
        self.maxDiff = 1000

    def test_create(self):
        self.points[2].state = 2
        self.points[2].payload = {'2': 4}
        self.points[2].dt_finish = datetime.utcnow()

        DRIVER.create_contract(self.contract1)
        DRIVER.create_contract(self.contract2)
        self.assertDictEqual(
            self.contract1.serialized,
            DRIVER.get_contract(self.contract1.uid).serialized)
        self.assertDictEqual(
            self.contract2.serialized,
            DRIVER.get_contract(self.contract2.uid).serialized)

    def test_delete(self):
        DRIVER.create_contract(self.contract1)
        DRIVER.create_contract(self.contract2)
        DRIVER.delete_contract(self.contract2.uid)


