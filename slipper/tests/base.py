# coding=utf-8

import unittest

from slipper.env import CFG


CFG()


class BaseTestCase(unittest.TestCase, object):

    def setUp(self):
        super(BaseTestCase, self).setUp()