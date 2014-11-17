# coding=utf-8

import unittest

from datetime import datetime
import uuid

from slipper.model.primitives import Contract, Point, compute_hash


class PointTestCase(unittest.TestCase, object):

    def setUp(self):
        self.uid = compute_hash('TEST')
        self.dt_activity = datetime.utcnow()
        self.fixture = Point(self.uid,
                             dt_activity=self.dt_activity)

    def test_serialize(self):
        fixture = {'state': None,
                   'uid': self.uid,
                   'dt_finish': None,
                   'worker': None,
                   'dt_activity': Point.to_timestamp(self.dt_activity),
                   'payload': None}
        self.assertEqual(fixture, self.fixture.serialized)

    def test_from_serialized(self):
        fixture = {'state': 35,
                   'worker': None,
                   'uid': self.uid,
                   'dt_finish': Point.to_timestamp(self.dt_activity),
                   'dt_activity': Point.to_timestamp(self.dt_activity),
                   'payload': None}
        self.assertDictEqual(fixture,
                             Point.from_serialized(fixture).serialized)


class TestBase(object):

    class ContainerTestBase(unittest.TestCase, object):

        def setUp(self):
            self.contract = self.get_contract()

        def get_contract(self):
            raise NotImplementedError('Child responsibility')

        def test_not_done_all_points_incomplete(self):
            """"""
            self.assertIsNone(self.contract.state)

        def test_done_all_points_success(self):
            for point in self.contract.points:
                point.state = 0
            self.assertEqual(self.contract.state, 0)

        def test_is_not_done_with_one_point_success(self):
            self.contract.points[0].state = 0
            self.assertIsNone(self.contract.state)

        def test_failed_if_all_complete_one_fail(self):
            for point in self.contract.points:
                point.state = 0
            self.contract.points[0].state = 2
            self.assertEqual(self.contract.state, 1)


class StrictContractTestCase(TestBase.ContainerTestBase):
    """Strict contracts behaviour."""

    def get_contract(self):
        return Contract(
            points=[Point(compute_hash(i)) for i in range(3)],
            timeout=30,
            route='strict',
            strict=True
        )

    def test_failed_if_all_incomplete_one_fail(self):
        self.contract.points[0].state = 2
        self.assertEqual(self.contract.state, 1)


class NonStrictContractTestCase(TestBase.ContainerTestBase):

    def get_contract(self):
        return Contract(
            points=[Point(compute_hash(i)) for i in range(3)],
            timeout=30,
        )

    def test_incomplete_if_all_incomplete_one_fail(self):
        self.contract.points[0].state = 2
        self.assertEqual(self.contract.state, None)


class ContractSignatureTestCase(unittest.TestCase):

    def setUp(self):
        self.points = [Point(compute_hash(i)) for i in range(6)]

    def test_different_points(self):
        c1 = Contract(
            points=self.points[:3],
            timeout=30,
        )
        c2 = Contract(
            points=self.points[2:],
            timeout=30,
        )
        self.assertNotEqual(c1.uid, c2.uid)

    def test_different_meta(self):
        c1 = Contract(
            points=self.points,
            timeout=30,
        )
        c2 = Contract(
            points=self.points,
            timeout=40,
        )
        self.assertNotEqual(c1.uid, c2.uid)
