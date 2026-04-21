
from unittest import TestCase
import prego


class Fail(TestCase):
    def test_fail_cmd(self):
        prego.init()
        test = prego.Task()
        test.command('false')
        prego.commit()
