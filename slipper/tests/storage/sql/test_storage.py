# coding=utf-8
from __future__ import absolute_import

from datetime import timedelta

from slipper.model import primitives
from slipper.model.identity import compute_hash
from slipper.storage.driver import DRIVER
from slipper.storage import exc

from slipper.tests.storage.sql.base import DBTestBase


class IntersectedTestCase(DBTestBase):

    def setUp(self):
        super(IntersectedTestCase, self).setUp()
        self.points = [primitives.Point() for _ in range(6)]
        self.contract1 = primitives.Contract(points=self.points[:3],
                                             timeout=30)
        self.contract2 = primitives.Contract(points=self.points[2:],
                                             timeout=30)

    def test_create(self):
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






class StorageTest(DBTestBase):




    def atest_create_delete(self):
        """Create and delete two contracts."""
        points = [primitives.Point(uid=compute_hash(d))
                  for d in ['a', 'b', 'c']]
        c1 = primitives.Contract(
            timeout=timedelta(hours=1).seconds,
            route='abs1',
            points=points,
        )
        c2 = primitives.Contract(
            timeout=timedelta(hours=1).seconds,
            points=points,
        )
        DRIVER.create_contract(c1)
        DRIVER.create_contract(c2)
        DRIVER.delete_contract(c1.uid, c1.sub_hash)
        with self.assertRaises(exc.NotFoundError):
            DRIVER.get_contract(c1.uid, c1.sub_hash)
        with self.assertRaises(exc.NotFoundError):
            DRIVER.delete_contract(c1.uid, c1.sub_hash)

    def atest_update_point(self):
        c = primitives.Contract(
            timeout=timedelta(hours=1).seconds,
            route='abs1',
            points=[primitives.Point(uid=compute_hash(d))
                    for d in ['a', 'b', 'c']],
        )
        DRIVER.create_contract(c)
        new_point = primitives.Point(uid=compute_hash('a'), state=34)
        DRIVER.update_point(new_point)
        res = DRIVER.get_contract(c.uid, c.sub_hash)
        for p in res.points:
            if p.uid == new_point.uid:
                self.assertEqual(p.state, 34)

    def stest_update_non_existent_point(self):
        with self.assertRaises(exc.NotFoundError):
            DRIVER.update_point(primitives.Point(uid=compute_hash('F')))
