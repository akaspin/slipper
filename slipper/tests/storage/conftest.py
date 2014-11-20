# coding=utf-8

import pytest

import uuid

from slipper.model.primitives import Contract, Point, compute_hash
from slipper.storage.driver import DRIVER as STORAGE


@pytest.fixture
def storage():
    """Storage driver. Recreate database."""
    try:
        STORAGE.boot()
    except:
        pass
    return STORAGE


@pytest.fixture(params=[
    [(0, 1), (2, 3)],
    [(0, 2), (2, 3)],
    [(0, 4), (3, 9)],
    [(0, 4), (3, 9), (2, 12)],
])
def contracts(request):
    """List of contracts."""
    inst = uuid.uuid4().hex
    rs = request.param
    min_ix = min(m for (m, _) in rs)
    max_ix = max(m for (_, m) in rs)
    points = [Point(compute_hash(inst, i))
              for i in range(min_ix, max_ix+1)]
    print rs, min_ix, max_ix
    return [Contract(points=points[l:r], timeout=30) for (l, r) in rs]


@pytest.yield_fixture
def contracts_in_storage(request, storage, contracts):
    """Contracts in storage"""
    for contract in contracts:
        storage.create_contract(contract)
    yield contracts

    for c in contracts:
        try:
            storage.delete_contract(c.uid)
        except:
            pass
