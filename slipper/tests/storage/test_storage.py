# coding=utf-8

import pytest

from datetime import datetime

from slipper.storage.exc import NotFoundError


def test_create_many(storage, contracts):
    """Create many contracts."""
    for contract in contracts:
        #> Create contract
        storage.create_contract(contract)

        #> Assert created contract is equal
        assert storage.get_contract(contract.uid).serialized == \
               contract.serialized


def test_delete(storage, contracts_in_storage):
    """Create contracts when delete all but first."""

    #> Delete first contract
    storage.delete_contract(contracts_in_storage[0].uid)

    #> Assert what deleted contract not found
    with pytest.raises(NotFoundError):
        storage.get_contract(contracts_in_storage[0].uid)

    #> Assert all non-deleted contracts are consistent
    for contract in contracts_in_storage[1:]:
        assert storage.get_contract(contract.uid).serialized == \
               contract.serialized


def test_update_point(storage, contracts_in_storage):

    #> modify one point
    contract = contracts_in_storage[1]
    point = contract.points[0]
    point.state = 2
    point.dt_finish = datetime.utcnow()

    #> And update it
    storage.update_point(point)

    #> Assert contract is updated
    assert storage.get_contract(contract.uid).serialized == \
           contract.serialized

