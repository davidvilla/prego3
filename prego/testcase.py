
import logging
import unittest

from .runner import init, Runner
from .exc import TestFailed
from .tools import StatusFilter
from .const import Status
from . import gvars


class PregoTestCase(object):
    def __init__(self, testcase, methodname):
        self.testcase = testcase
        self.methodname = methodname
        self.status = Status.NOEXEC

        self.name = "%s.%s" % (testcase.__class__.__name__, methodname)
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.INFO)
        self._status_filter = StatusFilter(self)
        self.log.addFilter(self._status_filter)
        init()

    def commit(self):
        __tracebackhide__ = True
        self.status = Status.UNKNOWN
        self.log.info(Status.indent('-') + ' $name BEGIN')
        try:
            Runner(gvars.tasks).run()
            self.status = Status.OK
        except TestFailed:
            self.status = Status.FAIL
            raise
        except Exception:
            self.status = Status.ERROR
            raise
        finally:
            self.log.info('$status  $name END')
            self.log.removeFilter(self._status_filter)
            init()


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
