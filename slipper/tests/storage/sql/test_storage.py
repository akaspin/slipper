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
        c1b, c1s = self.adapter.create_contract(c1, session=session)
        c2b, c2s = self.adapter.create_contract(c2, session=session)
        self.assertDictEqual(c1.base.serialized, c1b.serialized)
        self.assertDictEqual(c1.serialized, c1s.serialized)
        self.assertDictEqual(c2.serialized, c2s.serialized)
        self.assertIsNone(c2b)

    def test_create_delete(self):
        """Create contract when delete sub."""
        c = primitives.Contract(
            timeout=timedelta(hours=1).seconds,
            route='abs1',
            points=[primitives.Point(uid=compute_hash(d))
                    for d in ['a', 'b', 'c']],
        )
        self.adapter.create_contract(c)
        self.adapter.delete_contract(c.uid, c.sub_hash)
        with self.assertRaises(exc.NotFoundError):
            self.adapter.get_contract(c.uid, c.sub_hash)
        with self.assertRaises(exc.NotFoundError):
            self.adapter.delete_contract(c.uid, c.sub_hash)
        res = self.adapter.get_contract(c.base.uid, c.base.sub_hash)
        self.assertDictEqual(c.base.serialized, res.serialized)
        self.adapter.delete_contract(c.base.uid, c.base.sub_hash)
        with self.assertRaises(exc.NotFoundError):
            self.adapter.get_contract(c.base.uid, c.base.sub_hash)

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
