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

    def atest_create(self, session=None):
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

    def atest_create_delete(self):
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
        res = self.adapter.get_contract(c.base.uid, c.base.sub_hash)
        self.assertDictEqual(c.base.serialized, res.serialized)
        self.adapter.delete_contract(c.base.uid, c.base.sub_hash)
        with self.assertRaises(exc.NotFoundError):
            self.adapter.get_contract(c.base.uid, c.base.sub_hash)

    def test_update_point(self):
        p1 = primitives.Point(uid=compute_hash('1'))
        c = primitives.Contract(
            timeout=timedelta(hours=1).seconds,
            route='abs1',
            points=[p1] + [primitives.Point(uid=compute_hash(d))
                           for d in ['a', 'b', 'c']],
        )
        self.adapter.create_contract(c)
        p1.state = 34
        self.assertEqual(self.adapter.update_point(p1), 2)
        res = self.adapter.get_contract(c.uid, c.sub_hash)
        for p in res.points:
            if p.uid == p1.uid:
                self.assertEqual(p.state, 34)
