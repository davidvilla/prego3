# -*- coding: utf-8; mode: python -*-

from unittest import TestCase
import hamcrest

from .unit_tests import AssertionTest

import sys
sys.path.insert(0, '.')

import prego


class FileMatchers(TestCase, AssertionTest):
    def test_file_exists(self):
        c = self.assert_that(prego.File('/etc/fstab'), prego.exists())
        c.eval()

    def test_file_exists_in_cwd(self):
        prego.init()
        t = prego.Task()
        t.assert_that(prego.File('test/$testfilename'), prego.exists())
        prego.commit()

    def test_file_exists_fails(self):
        c = self.assert_that(prego.File('/etc/missing'), prego.exists())

        with self.assertRaises(prego.PregoAssertionFailed):
            c.eval()

    def test_file_do_not_exists(self):
        c = self.assert_that(prego.File('/etc/missing'),
                             hamcrest.is_not(prego.exists()))
        c.eval()

    def test_file_contains(self):
        open('/tmp/prego-content', 'wt').write('this a sample file for prego')
        prego.init()
        t = prego.Task()
        t.assert_that(prego.File('/tmp/prego-content').content,
                      hamcrest.contains_string('sample file'))
        prego.commit()

    def test_non_exising_file_contains(self):
        prego.init()
        t = prego.Task()
        t.assert_that(prego.File('/tmp/kk').content,
                      hamcrest.is_not(hamcrest.contains_string('SOMETHING')))
        prego.commit()

    def test_file_contains_fail(self):
        c = self.assert_that(prego.File('/etc/fstab').content,
                             hamcrest.contains_string('missing'))

        with self.assertRaises(prego.PregoAssertionFailed):
            c.eval()

    def test_file_permissions(self):
        prego.init()
        t = prego.Task()
        t.assert_that(prego.File('/etc/fstab'), prego.has_permissions(0o644))
        t.assert_that(prego.File('/etc/fstab'), prego.has_permissions(0o200))
        t.assert_that(prego.File('/etc/fstab'), prego.has_permissions(0o400))
        t.assert_that(prego.File('/etc/fstab'), prego.has_permissions(0o440))
        t.assert_that(prego.File('/etc/fstab'), prego.has_permissions(0o004))
        prego.commit()

    def test_file_compare(self):
        prego.init()
        a = prego.File('/etc/passwd')
        b = prego.File('/etc/fstab')

        t = prego.Task()
        t.assert_that(a, hamcrest.is_not(b))
        prego.commit()

    def test_file_compare2(self):

        with open('/tmp/a', 'w') as fd:
            fd.write("foobar")

        with open('/tmp/b', 'w') as fd:
            fd.write("foobar")

        prego.init()
        t = prego.Task()
        t.assert_that(prego.File('/tmp/a'), hamcrest.is_(prego.File('/tmp/b')))
        prego.commit()

    def test_file_compare_fail(self):
        prego.init()
        t = prego.Task()
        t.assert_that(prego.File('/etc/fstab'), hamcrest.is_not(prego.File('/etc/passwd')))
        prego.commit()
