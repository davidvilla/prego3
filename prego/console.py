# -*- coding:utf-8; tab-width:4; mode:python -*-

import sys
import os
import time
import logging
import argparse

from logging import StreamHandler

import pytest

from commodity.log import NullHandler
from commodity.args import parser, add_argument, args

from . import config
from .tools import set_logger_default_formatter, StatusFilter, update_obj
from . import const

logging.getLogger().addFilter(StatusFilter())


class _PregoReporter:
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._start = None
        self._passed = 0
        self._failed = 0
        self._n_results = 0

    @pytest.hookimpl
    def pytest_sessionstart(self, session):
        self._start = time.time()

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            if report.passed:
                self._passed += 1
            elif report.failed:
                self._failed += 1
            if not self._verbose:
                char = 'F' if report.failed else '.'
                print(char, end='', file=sys.stderr, flush=True)
                self._n_results += 1

    @pytest.hookimpl
    def pytest_sessionfinish(self, session, exitstatus):
        elapsed = time.time() - self._start
        total = self._passed + self._failed
        if not self._verbose and self._n_results:
            print(file=sys.stderr)
        noun = 'test' if total == 1 else 'tests'
        print('-' * 70, file=sys.stderr)
        print(f'Ran {total} {noun} in {elapsed:.3f}s', file=sys.stderr)
        if self._failed:
            print(f'\nFAILED (failures={self._failed})', file=sys.stderr)
        else:
            print('\nOK', file=sys.stderr)


def run():
    parser.prog = 'prego'

    # behaviour
    parser.add_argument('-c', '--config', metavar='FILE',
                        help='explicit config file')
    parser.add_argument('-k', '--keep-going', action='store_true',
                        help="continue even with failed assertion or tests")
    parser.add_argument('-d', '--dirty', action='store_true',
                        help="do not remove generated files")

    # output
    parser.add_argument('-o', '--stdout', action='store_true',
                        help='print tests stdout')
    parser.add_argument('-e', '--stderr', action='store_true',
                        help='print tests stderr')
    parser.add_argument('-t', '--time-tag', dest='timetag', action='store_true',
                        help='Include time info in logs')

    parser.add_argument('-v', '--verbose', dest='verbosity', action='count',
                        help='increase log verbosity')

    # styling
    parser.add_argument('-p', '--plain', action='store_false', dest='color',
                        help='avoid colors and styling in output')
    parser.add_argument('-f', '--force-color', action='store_true', dest='force_color',
                        help='force colors and styling in output')

    # pass through pytest options
    parser.add_argument('pytest_args', metavar='pytest-args', nargs=argparse.REMAINDER)

    parser.load_config_file(const.PREGO_CMD_DEFAULTS)
    parser.parse_args()

    for x in range(args.pytest_args.count('--')):
        args.pytest_args.remove('--')

    if args.config:
        parser.load_config_file(os.path.abspath(args.config))
    else:
        parser.load_config_file(const.USER_CONFIG)
        parser.load_config_file(const.CWD_CONFIG)

    update_obj(config, args)

    pytest_opts = ['-p', 'no:terminalreporter']
    extra_plugins = [_PregoReporter(verbose=bool(config.verbosity))]

    if config.verbosity:
        pytest_opts += ['-p', 'no:logging', '--capture=no']

        if config.verbosity == 1:
            loglevel = logging.INFO
        elif config.verbosity >= 2:
            loglevel = logging.DEBUG

        if config.verbosity > 2:
            config.stderr = config.stdout = True

        root = logging.getLogger()
        root.setLevel(loglevel)

        handler = StreamHandler()
        root.addHandler(handler)
        set_logger_default_formatter(root)

    if config.force_color:
        logging.warning("Option -f/--force-color is deprecated")
        sys.exit(1)

    sys.exit(pytest.main(pytest_opts + args.pytest_args, plugins=extra_plugins))
