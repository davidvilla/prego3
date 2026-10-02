
import unittest

from .runner import init, commit
from . import gvars


class PregoTestCase(object):
    def __init__(self, testcase, methodname):
        self.testcase = testcase
        self.methodname = methodname
        init()

    def commit(self):
        __tracebackhide__ = True
        commit()


class TestCase(unittest.TestCase):
    def run(self, result=None):
        method = getattr(self, self._testMethodName)
        gvars.testpath = method.__code__.co_filename
        self.prego_case = PregoTestCase(self, self._testMethodName)
        return super().run(result)

    # tools.set_testpath() expects the test method frame right below this one
    def _callTestMethod(self, method):
        __tracebackhide__ = True
        method()
        self.prego_case.commit()
