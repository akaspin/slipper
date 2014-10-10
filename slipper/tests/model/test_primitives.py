# coding=utf-8

import unittest

from datetime import datetime

from slipper.model.identity import compute_hash
from slipper.model.primitives import Contract, Point


class PointTestCase(unittest.TestCase, object):

    def setUp(self):
        self.name = 'test'
        self.dt_activity = datetime.utcnow()
        self.fixture = Point(compute_hash(self.name),
                             dt_activity=self.dt_activity)

    def test_serialize(self):
        fixture = {'state': None,
                   'uid': compute_hash(self.name),
                   'dt_finish': None,
                   'worker': None,
                   'dt_activity': Point.to_timestamp(self.dt_activity),
                   'payload': None}
        self.assertEqual(fixture, self.fixture.serialized)

    def test_from_serialized(self):
        fixture = {'state': 35,
                   'worker': None,
                   'uid': compute_hash(self.name),
                   'dt_finish': Point.to_timestamp(self.dt_activity),
                   'dt_activity': Point.to_timestamp(self.dt_activity),
                   'payload': None}
        self.assertDictEqual(fixture,
                             Point.from_serialized(fixture).serialized)


class ContractTestCase(unittest.TestCase, object):

    def setUp(self):
        self.regular = Contract(
            points=[Point(compute_hash(i)) for i in ['a', 'b', 'c']],
            timeout=30
        )
        self.strict = Contract(
            points=[Point(compute_hash(i)) for i in ['a', 'b', 'c']],
            timeout=30,
            strict=True,
            route='strict'
        )

    def test_is_base(self):
        self.assertTrue(self.regular.is_base)
        self.assertFalse(self.strict.is_base)

    def test_regular_is_done(self):
        self.assertFalse(self.regular.is_done)
        for p in self.regular.points:
            p.state = 0
        self.assertTrue(self.regular.is_done)

    def test_strict_is_done(self):
        self.strict.points[0].state = 34
        self.assertTrue(self.strict.is_done)
