# coding=utf-8

import pytest

from slipper.env import CFG

@pytest.mark.tryfirst
@pytest.fixture(scope='session', autouse=True)
def config():
    CFG()
