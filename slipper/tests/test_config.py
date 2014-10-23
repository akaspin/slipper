# coding=utf-8

from slipper.tests.base import BaseTestCase
from slipper.env import CFG


class ConfigTest(BaseTestCase):

    def test_peek(self):
        self.assertEqual(CFG['storage'].url,
                         CFG.storage.url)
