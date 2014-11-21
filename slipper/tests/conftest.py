# coding=utf-8

import pytest

from slipper.env import CFG


def pytest_addoption(parser):
    # Functional test
    parser.addoption('--fn', action='store_true', dest='fn', default=False,
                     help='Run functional tests.')
    parser.addoption('--slipper-instances', action='store', default=2,
                     help='Slipper instances.')


def pytest_runtest_setup(item):
    if 'fn' in item.keywords and \
            not item.config.getoption("fn"):
        pytest.skip("need --fn option to run")


@pytest.mark.tryfirst
@pytest.fixture(scope='session', autouse=True)
def config():
    CFG()
