# coding=utf-8
from __future__ import absolute_import

from datetime import timedelta

from slipper.model import primitives
from slipper.model.identity import compute_hash
from slipper.storage.interface import interface
from slipper.storage import exc

from slipper.tests.storage.sql.base import DBTestBase


class StorageTest(DBTestBase):

    def setUp(self):
        super(StorageTest, self).setUp()
        self.adapter = interface.adapter

    def test_create(self, session=None):
        c1 = primitives.Contract(
            timeout=timedelta(hours=1).seconds,
            route='abs',
            points=[primitives.Point(uid=compute_hash(d))
                    for d in ['a', 'b', 'c']],
        )
        c2 = primitives.Contract(
            timeout=timedelta(hours=1).seconds,
            route='abs1',
            points=[primitives.Point(uid=compute_hash(d))
                    for d in ['a', 'b', 'c']],
        )
        self.adapter.create_contract(c1, session=session)
        self.adapter.create_contract(c2, session=session)
        self.assertEqual(c1.serialized, self.adapter.get_contract(
            c1.uid, c1.sub_hash).serialized)
        self.assertEqual(c2.serialized, self.adapter.get_contract(
            c2.uid, c2.sub_hash).serialized)


    def test_create_delete(self):
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
        self.adapter.create_contract(c1)
        self.adapter.create_contract(c2)
        self.adapter.delete_contract(c1.uid, c1.sub_hash)
        with self.assertRaises(exc.NotFoundError):
            self.adapter.get_contract(c1.uid, c1.sub_hash)
        with self.assertRaises(exc.NotFoundError):
            self.adapter.delete_contract(c1.uid, c1.sub_hash)

    def test_update_point(self):
        c = primitives.Contract(
            timeout=timedelta(hours=1).seconds,
            route='abs1',
            points=[primitives.Point(uid=compute_hash(d))
                    for d in ['a', 'b', 'c']],
        )
        self.adapter.create_contract(c)
        new_point = primitives.Point(uid=compute_hash('a'), state=34)
        self.adapter.update_point(new_point)
        res = self.adapter.get_contract(c.uid, c.sub_hash)
        for p in res.points:
            if p.uid == new_point.uid:
                self.assertEqual(p.state, 34)

    def test_update_non_existent_point(self):
        with self.assertRaises(exc.NotFoundError):
            self.adapter.update_point(primitives.Point(uid=compute_hash('F')))
