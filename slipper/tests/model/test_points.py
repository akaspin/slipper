# coding=utf-8

import pytest

from datetime import datetime

from slipper.model.primitives import compute_hash, Point, Contract


class TestPoint(object):
    NOW = datetime.utcnow()
    UID = compute_hash('TEST')

    @property
    @pytest.fixture(scope='class')
    def point(self):
        return Point(self.UID, dt_activity=self.NOW)

    @property
    @pytest.fixture
    def serialized_point(self):
        return {'state': None,
                'uid': self.UID,
                'dt_finish': None,
                'worker': None,
                'dt_activity': Point.to_timestamp(self.NOW),
                'payload': None}

    def test_serialize(self):
        assert self.point.serialized == self.serialized_point

    def test_deserealize(self):
        assert Point.from_serialized(
            self.serialized_point).serialized == self.serialized_point
