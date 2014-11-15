# coding=utf-8

import unittest

from slipper.model.primitives import compute_hash


class UIDTest(unittest.TestCase, object):

    def test_multi(self):
        self.assertEqual(compute_hash('a', 'b', 'c'),
                         compute_hash(*['a', 'b', 'c']))
