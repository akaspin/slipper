# coding=utf-8
"""Init infrastructure."""

import os

from slipper.env import CFG
from slipper.storage.driver import DRIVER


CFG(os.environ.get('SLIPPER_CONFIG'))


def main():
    DRIVER.boot()


if __name__ == '__main__':

    main()