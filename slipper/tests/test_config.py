# coding=utf-8

import unittest

from slipper.env import CFG


class ConfigTest(unittest.TestCase, object):

    def test_peek(self):
        self.assertEqual(CFG['storage'].use,
                         CFG.storage.use)
