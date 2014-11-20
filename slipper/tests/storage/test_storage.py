# coding=utf-8

import pytest

from datetime import datetime

from slipper.storage.exc import NotFoundError


def test_create_many(storage, contracts):
    """Create many contracts."""
    for contract in contracts:
        storage.create_contract(contract)
        assert storage.get_contract(contract.uid).serialized == \
               contract.serialized
        storage.delete_contract(contract.uid)


def test_delete(storage, contracts_in_storage):
    """Create contracts when delete all but first."""

    for i, contract in enumerate(contracts_in_storage):
        storage.delete_contract(contract.uid)
        with pytest.raises(NotFoundError):
            storage.get_contract(contract.uid)

        for stale in contracts_in_storage[i+1:]:
            assert storage.get_contract(stale.uid).serialized == \
                   stale.serialized


def test_update_point(storage, contracts_in_storage):
    contract = contracts_in_storage[1]
    point = contract.points[0]
    point.state = 2
    point.dt_finish = datetime.utcnow()
    storage.update_point(point)
    assert storage.get_contract(contract.uid).serialized == \
           contract.serialized
