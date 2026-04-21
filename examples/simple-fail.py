
from prego import TestCase, Task


class Fail(TestCase):
    def test_fail_cmd(self):
        task = Task()
        task.command('false')
