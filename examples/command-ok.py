# -*- coding:utf-8; tab-width:4; mode:python -*-

from prego import TestCase, Task


class OK(TestCase):
    def test_true_cmd(self):
        test = Task()
        test.command('true')
