# -*- coding:utf-8; tab-width:4; mode:python -*-

from unittest import TestCase

import prego


class Test(TestCase):
    def test_cmd_fail(self):
        self.fail()

    def test_cmd_true(self):
        prego.init()
        task = prego.Task()
        task.command('true')
        prego.commit()

    def test_cmd_wrong_true_and_ls(self):
        prego.init()
        task = prego.Task()
        task.command('wrong')
        task.command('true')

        task2 = prego.Task()
        task2.command('ls')
        prego.commit()

    def test_cmd_false_true(self):
        prego.init()
        task = prego.Task()
        task.command('false')
        task.command('true')
        prego.commit()

    def test_cmd_fail_with_outs(self):
        prego.init()
        task = prego.Task()
        task.command('echo STDOUT')
        task.command('echo STDERR >&2')
        task.command('false')
        prego.commit()
