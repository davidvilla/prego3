# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase


class Fail(TestCase):
    def test_fail(self):
        self.fail()
