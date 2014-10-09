# coding=utf-8
from __future__ import absolute_import

from datetime import datetime, timedelta

from .base import DBTestBase
from ..model import primitives
from ..storage.interface import interface
from ..model.identity import compute_hash


class StorageTest(DBTestBase):

    def test_create(self, session=None):
        adapter = interface.adapter
        adapter.create_contract(primitives.Contract(
            # uid=compute_hash('abs'),
            timeout=timedelta(hours=1).seconds,
            points=[primitives.Point(uid=compute_hash(d))
                       for d in ['a', 'b', 'c']],
            # routing_key='a')
        ), session=session)
        adapter.create_contract(primitives.Contract(
            # uid=compute_hash('abs'),
            timeout=timedelta(hours=1).seconds,
            points=[primitives.Point(uid=compute_hash(d))
                       for d in ['a', 'b', 'c', 'd']],
            routing='a'
        ), session=session)
