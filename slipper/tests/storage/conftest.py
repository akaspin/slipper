# coding=utf-8

import pytest

from slipper.model.primitives import Contract, Point, compute_hash
from slipper.storage.driver import DRIVER as STORAGE


@pytest.fixture
def storage():
    """Storage driver. Recreate database."""
    STORAGE.cleanup()
    STORAGE.boot()
    return STORAGE


@pytest.fixture(params=[
    [(0, 4), (3, 9)],
    [(0, 4), (3, 9), (2, 12)],
])
def contracts(request):
    """List of contracts."""
    rs = request.param
    min_ix = min(m for (m, _) in rs)
    max_ix = max(m for (_, m) in rs)
    points = [Point(compute_hash(i)) for i in range(min_ix, max_ix+1)]
    return [Contract(points=points[l:r], timeout=30) for (l, r) in rs]


@pytest.fixture
def contracts_in_storage(storage, contracts):
    """Contracts in storage"""
    for contract in contracts:
        #> Create contract
        storage.create_contract(contract)
    return contracts