# -*- coding:utf-8; tab-width:4; mode:python -*-
"""
Example tests to check prego output
"""

from prego import TestCase, Task


class multiline_commands(TestCase):
    def test_writing_out(self):
        task = Task()
        task.command('echo -e "hi\nbye\nagain"')

    def test_writing_err(self):
        task = Task()
        task.command('echo -e "hi\nbye\nagain" >&2')
