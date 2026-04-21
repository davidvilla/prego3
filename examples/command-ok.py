
from prego import TestCase, Task


class OK(TestCase):
    def test_true_cmd(self):
        test = Task()
        test.command('true')
