
from unittest import TestCase


class Fail(TestCase):
    def test_fail(self):
        self.fail()
