# -*- coding:utf-8; tab-width:4; mode:python -*-

import sys
import logging
import unittest
import contextlib
import time

from commodity.path import child_relpath

from .runner import init, Runner
from .exc import TestFailed
from .tools import StatusFilter
from .const import Status, term
from . import gvars


class PregoTestCase(object):
    def __init__(self, testcase, methodname, testpath):
        self.testcase = testcase
        self.methodname = methodname
        self.status = Status.NOEXEC

        self.name = "%s:%s.%s" % (child_relpath(testpath), testcase.__class__.__name__, methodname)
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.INFO)
        self.log.addFilter(StatusFilter(self))
        init()

    def commit(self):
        self.status = Status.UNKNOWN
        self.log.info(Status.indent('=') + term().reverse(' INI ') + ' $name')
        try:
            Runner(gvars.tasks).run()
            self.status = Status.OK
        except TestFailed as test_failed:
            self.status = Status.FAIL
            raise test_failed  # shrink traceback
        except Exception:
            self.status = Status.ERROR
            raise
        finally:
            self.log.info('$status ' + term().reverse(' END ') + ' $name')
            init()

# patched unittest.case.TestCase (Python-3.12.8)
class TestCase(unittest.TestCase):
    def _callSetUp(self, testMethod=None):
        if testMethod:
            gvars.testpath = testpath = testMethod.__code__.co_filename
            self.prego_case = PregoTestCase(self, self._testMethodName, testpath)
        unittest.TestCase._callSetUp(self)

    def _callTestMethod(self, method):
        method()
        self.prego_case.commit()

    def run(self, result=None):
        if result is None:
            result = self.defaultTestResult()
            startTestRun = getattr(result, 'startTestRun', None)
            stopTestRun = getattr(result, 'stopTestRun', None)
            if startTestRun is not None:
                startTestRun()
        else:
            stopTestRun = None

        result.startTest(self)
        try:
            testMethod = getattr(self, self._testMethodName)
            if (getattr(self.__class__, "__unittest_skip__", False) or
                getattr(testMethod, "__unittest_skip__", False)):
                # If the class or method was skipped.
                skip_why = (getattr(self.__class__, '__unittest_skip_why__', '')
                            or getattr(testMethod, '__unittest_skip_why__', ''))
                _addSkip(result, self, skip_why)
                return result

            expecting_failure = (
                getattr(self, "__unittest_expecting_failure__", False) or
                getattr(testMethod, "__unittest_expecting_failure__", False)
            )
            outcome = _Outcome(result)
            start_time = time.perf_counter()
            try:
                self._outcome = outcome

                with outcome.testPartExecutor(self):
                    self._callSetUp(testMethod)  # PREGO PATCHED!!!!
                if outcome.success:
                    outcome.expecting_failure = expecting_failure
                    with outcome.testPartExecutor(self):
                        self._callTestMethod(testMethod)
                    outcome.expecting_failure = False
                    with outcome.testPartExecutor(self):
                        self._callTearDown()
                self.doCleanups()
                self._addDuration(result, (time.perf_counter() - start_time))

                if outcome.success:
                    if expecting_failure:
                        if outcome.expectedFailure:
                            self._addExpectedFailure(result, outcome.expectedFailure)
                        else:
                            self._addUnexpectedSuccess(result)
                    else:
                        result.addSuccess(self)
                return result
            finally:
                # explicitly break reference cycle:
                # outcome.expectedFailure -> frame -> outcome -> outcome.expectedFailure
                outcome.expectedFailure = None
                outcome = None

                # clear the outcome, no more needed
                self._outcome = None

        finally:
            result.stopTest(self)
            if stopTestRun is not None:
                stopTestRun()


# patched unittest.case._Outcome (Python-3.12.8)
class _Outcome(unittest.case._Outcome):

    @contextlib.contextmanager
    def testPartExecutor(self, test_case, subTest=False):
        old_success = self.success
        self.success = True
        try:
            yield
        except KeyboardInterrupt:
            raise
        except unittest.case.SkipTest as e:
            self.success = False
            unittest.case._addSkip(self.result, test_case, str(e))
        except unittest.case._ShouldStop:
            pass
        except:
            exc_info = list(sys.exc_info())

            ## begin prego patch
            if exc_info[0] == TestFailed:
                exc_info[2] = None  # remove traceback
            ## end prego patch

            if self.expecting_failure:
                self.expectedFailure = exc_info
            else:
                self.success = False
                if subTest:
                    self.result.addSubTest(test_case.test_case, test_case, exc_info)
                else:
                    unittest.case._addError(self.result, test_case, exc_info)
            # explicitly break a reference cycle:
            # exc_info -> frame -> exc_info
            exc_info = None
        else:
            if subTest and self.success:
                self.result.addSubTest(test_case.test_case, test_case, None)
        finally:
            self.success = self.success and old_success
