# -*- coding:utf-8; tab-width:4; mode:python -*-

from signal import SIGINT
from unittest import TestCase

from hamcrest import is_not, contains_string
from prego import *


# class TestDummyBool(TestCase):
#     def test_set_true(self):
#         port = 1234
#         proxy = "test -t:tcp -p {0}".format(port)
#
#         dummy = Test(desc='dummy bool',
#                      cwd='$basedir/dummies',
#                      detach=True,
#                      save_stderr=True, signal=SIGINT)
#         dummy.assert_that(localhost, is_not(listen_port(port)))
#         dummy.set_cmd('./duo-dummy-bool --host localhost --port {0} --id test --no-gui W'.format(port))
#         dummy.assert_that(StdErr().content,
#                           contains_string('-> set(True'))
#
#         client = Test(desc='bool client',
#                       cwd='$basedir/clients')
#         client.wait_that(localhost, listen_port(port), each=.05)
#         client.set_cmd("./duo-client-bool '{0}' --set True".format(proxy))
#
#
#     def test_active(self):
#         istaf_port = 11000
#
#         istaf = Test(desc='ISTAF', detach=True, timeout=None,
#                      cwd='$basedir/dummies',
#                      signal=SIGINT, expected=-SIGINT)
#         istaf.assert_that(localhost, is_not(listen_port(istaf_port)))
#         istaf.set_cmd('./duo-launch-istaf')
#
#         active_port = 1234
#         active_proxy = "test -t:tcp -p {0}".format(active_port)
#
#         active = Test(desc='active actor', detach=True, timeout=None,
#                       cwd='$basedir/dummies',
#                       signal=SIGINT)
#         active.assert_that(localhost, is_not(listen_port(active_port)))
#         active.wait_that(localhost, listen_port(istaf_port))
#         active.set_cmd('./duo-dummy-bool --host localhost --port {0} --id test --no-gui RWA'.format(active_port))
#         active.assert_that(StdErr().content,
#                            contains_string('-> set(True'))
#
#         observer_port = 1235
#         observer = Test(desc='observer', detach=True, timeout=None,
#                         cwd='$basedir/dummies',
#                         signal=SIGINT)
#         observer.assert_that(localhost, is_not(listen_port(observer_port)))
#         observer.wait_that(localhost, listen_port(active_port))
#         observer.set_cmd("./duo-dummy-bool --active-suscribe '{}' --host localhost --port {} --id test --no-gui W". format(active_proxy, observer_port))
#         observer.assert_that(StdErr().content,
#                              contains_string('-> set(True'))
#
#         client = Test(desc='client', cwd='$basedir/clients')
#         client.wait_that(localhost, listen_port(active_port))
#         client.wait_that(localhost, listen_port(observer_port))
#         client.set_cmd("./duo-client-bool '{0}' --set True".format(active_proxy))
