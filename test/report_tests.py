from hamcrest import contains_string, is_not
from prego import TestCase, Task

prego_cmd = 'bin/prego %s -c /dev/null'


class TestOutOptions(TestCase):
    def test_print_outs_on_fail(self):
        task = Task()
        task.command(prego_cmd % '-pveo examples/examples.py::Test::test_cmd_fail_with_outs', expected=1)
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("A.0.out| STDOUT"))

        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("A.3.err| STDERR"))

    def test_do_not_print_outs_on_fail(self):
        task = Task()
        task.command(prego_cmd % '-p examples/examples.py::Test::test_cmd_fail_with_outs', expected=1)
        task.assert_that(task.lastcmd.stderr.content,
                         is_not(contains_string("A.0.out| STDOUT")))

        task.assert_that(task.lastcmd.stderr.content,
                         is_not(contains_string("A.3.err| STDERR")))


class TestBeginEnd(TestCase):
    def test_begin_uses_pytest_nodeid(self):
        task = Task()
        task.command('bin/prego -pv examples/skip.py::Skip::test_ok', expected=0)
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("------  BEGIN examples/skip.py::Skip::test_ok"))

    def test_end_reports_ok_status(self):
        task = Task()
        task.command('bin/prego -pv examples/skip.py::Skip::test_ok', expected=0)
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("[ OK ]  END   examples/skip.py::Skip::test_ok"))

    def test_end_reports_fail_status(self):
        task = Task()
        task.command('bin/prego -pv examples/examples.py::Test::test_cmd_false_true', expected=1)
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("[FAIL]  END   examples/examples.py::Test::test_cmd_false_true"))

    def test_begin_end_not_shown_on_pass_without_verbose(self):
        task = Task()
        task.command('bin/prego -p examples/skip.py::Skip::test_ok', expected=0)
        task.assert_that(task.lastcmd.stderr.content, is_not(contains_string("BEGIN")))
        task.assert_that(task.lastcmd.stderr.content, is_not(contains_string("END")))

    def test_summary_on_pass(self):
        task = Task()
        task.command('bin/prego -p examples/skip.py::Skip::test_ok', expected=0)
        task.assert_that(task.lastcmd.stderr.content, contains_string("Ran 1 test in"))
        task.assert_that(task.lastcmd.stderr.content, contains_string("\nOK\n"))

    def test_summary_on_fail(self):
        task = Task()
        task.command('bin/prego -p examples/examples.py::Test::test_cmd_false_true', expected=1)
        task.assert_that(task.lastcmd.stderr.content, contains_string("FAILED (failures=1)"))


class TestSkip(TestCase):
    def test_skipped_tests_are_reported(self):
        task = Task()
        task.command('bin/prego -p examples/skip.py', expected=0)
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("sss"))
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("OK (skipped=3)"))

    def test_skip_reasons_are_logged_in_verbose_mode(self):
        task = Task()
        task.command('bin/prego -pv examples/skip.py', expected=0)
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("SKIP  examples/skip.py::Skip::test_skip_unittest (Skipped: not needed)"))
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("SKIP  examples/skip.py::Skip::test_skip_mark (Skipped: disabled)"))
        task.assert_that(task.lastcmd.stderr.content,
                         contains_string("SKIP  examples/skip.py::Skip::test_skip_inline (Skipped: skipped at runtime)"))
