# coding=utf-8
import pytest

from slipper.model.primitives import Contract, compute_hash, Point


class TestContract(object):
    @pytest.fixture(params=[True, False])
    def contract(self, request):
        return Contract(
            points=[Point(compute_hash(i)) for i in range(3)],
            timeout=30,
            route='route',
            strict=request.param
        )

    def test_not_done_all_points_incomplete(self, contract):
        assert contract.state is None

    def test_done_all_points_success(self, contract):
        for point in contract.points:
            point.state = 0
        assert contract.state == 0

    def test_is_not_done_with_one_point_success(self, contract):
        contract.points[0].state = 0
        assert contract.state is None

    def test_failed_if_all_complete_one_fail(self, contract):
        for point in contract.points:
            point.state = 0
        contract.points[0].state = 2
        assert contract.state == 1

    def test_if_all_incomplete_one_fail(self, contract):
        contract.points[0].state = 2
        assert contract.state == (1 if contract.strict else None)