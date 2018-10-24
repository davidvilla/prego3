# -*- coding:utf-8; tab-width:4; mode:python -*-

from prego import TestCase, Task, AUTO


class OK(TestCase):
    def test_echo(self):
        Task().command('echo this goes to stdout')

    def test_ls_stdout(self):
        Task().command('ls /etc/pass*')

    def test_ls_stdout_auto(self):
        Task().command('ls /etc/pass*', stdout=AUTO)

    def test_ls_stderr(self):
        Task().command('ls /etc/pass* >&2')

    def test_ls_stderr_auto(self):
        Task().command('ls /etc/pass* >&2', stderr=AUTO)
