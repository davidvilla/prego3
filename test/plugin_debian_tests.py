
from hamcrest import is_not

from prego import Task, TestCase
from prego.debian import Package, installed


class Debian(TestCase):
    def test_installed(self):
        depends = Task()
        depends.assert_that(Package('bash'), installed())
        depends.assert_that(Package('never-installed'),
                            is_not(installed()))

    def test_installed_version(self):
        depends = Task()
        depends.assert_that(Package('bash'),
                            installed(min_version='3.0'))
