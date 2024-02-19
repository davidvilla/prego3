# -*- coding:utf-8; tab-width:4; mode:python -*-

import sys
import logging
import unittest
import contextlib
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


class TestCase(unittest.TestCase):
    def _callSetUp(self, testMethod=None):
        if testMethod:
            gvars.testpath = testpath = testMethod.__code__.co_filename
            self.prego_case = PregoTestCase(self, self._testMethodName, testpath)
        super()._callSetUp()

    def _callTestMethod(self, method):
        super()._callTestMethod(method)
        self.prego_case.commit()

    def _callTearDown(self):
        super()._callTearDown()

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
            try:
                self._outcome = outcome

                with outcome.testPartExecutor(self):
                    self._callSetUp(testMethod)  ## this is the only line changed
                if outcome.success:
                    outcome.expecting_failure = expecting_failure
                    with outcome.testPartExecutor(self):
                        self._callTestMethod(testMethod)
                    outcome.expecting_failure = False
                    with outcome.testPartExecutor(self):
                        self._callTearDown()
                self.doCleanups()

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



# patched unittest.case._Outcome
class _Outcome(object):
    def __init__(self, result=None):
        self.expecting_failure = False
        self.result = result
        self.result_supports_subtests = hasattr(result, "addSubTest")
        self.success = True
        self.skipped = []
        self.expectedFailure = None
        self.errors = []

    @contextlib.contextmanager
    def testPartExecutor(self, test_case, isTest=False):
        old_success = self.success
        self.success = True
        try:
            yield
        except KeyboardInterrupt:
            raise
        except unittest.case.SkipTest as e:
            self.success = False
            self.skipped.append((test_case, str(e)))
        except unittest.case._ShouldStop:
            pass
        except:
            exc_info = list(sys.exc_info())
            if exc_info[0] == TestFailed:
                exc_info[2] = None  # remove traceback

            if self.expecting_failure:
                self.expectedFailure = exc_info
            else:
                self.success = False
                self.errors.append((test_case, exc_info))
            # explicitly break a reference cycle:
            # exc_info -> frame -> exc_info
            exc_info = None
        else:
            if self.result_supports_subtests and self.success:
                self.errors.append((test_case, None))
        finally:
            self.success = self.success and old_success
