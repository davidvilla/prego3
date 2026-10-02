import unittest

import pytest

import prego


class Skip(prego.TestCase):
    @unittest.skip("not needed")
    def test_skip_unittest(self):
        prego.Task().command('false')

    @pytest.mark.skip(reason="disabled")
    def test_skip_mark(self):
        prego.Task().command('false')

    def test_skip_inline(self):
        pytest.skip("skipped at runtime")

    def test_ok(self):
        prego.Task().command('true')
