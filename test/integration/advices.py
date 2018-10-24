# -*- coding:utf-8; tab-width:4; mode:python -*-

from signal import SIGTERM

from prego import TestCase, Task


class Timeout(TestCase):
    def test_no_detach_no_timeout(self):
        task = Task()
        task.command('cat', signal=SIGTERM, expected=-SIGTERM, timeout=None)

    def test_no_detach_no_timeout2(self):
        task = Task()
        task.command('cat', signal=SIGTERM, expected=-SIGTERM, timeout=None)
