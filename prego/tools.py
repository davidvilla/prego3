# -*- coding:utf-8; tab-width:4; mode:python -*-

import sys
import os
import string
import socket
import traceback
import logging

import configobj
import validate
import six
import io

from commodity.log import CapitalLoggingFormatter
from commodity.pattern import Bunch

from . import gvars
from .const import PREGO_TMP_BASE, PREGO_TMP, term, PREGO_SPECS

if six.PY2:
    file_types = file, io.IOBase
else:
    file_types = (io.IOBase,)

basedir = os.getcwd()


class Interpolator(object):
    fixed_vars = Bunch(dict(
        basedir      = os.path.relpath(basedir),
        fullbasedir  = os.path.abspath(basedir),
        pid          = os.getpid(),
        tmpbase      = PREGO_TMP_BASE,
        tmp          = PREGO_TMP,
        hostname     = socket.gethostname(),
        ))

    def __init__(self):
        self.vars = self.fixed_vars.copy()
        self.vars.update(gvars.context)
        set_testpath()

        if not gvars.testpath:
            print("ERROR: $testdir, $fulltestdir and $testfilename not available in this context")
            return

        testdir, testname = os.path.split(gvars.testpath)
        self.vars.update(
            dict(
                testdir      = os.path.relpath(testdir),
                fulltestdir  = os.path.abspath(testdir),
                testfilename = testname,
            ))

    def apply(self, text):
        if not isinstance(text, six.string_types):
            return text

        return string.Template(text).safe_substitute(self.vars)


def create_file(fpath, *args):
    path, name = os.path.split(fpath)
    if path in [PREGO_TMP, PREGO_TMP_BASE]:
        try:
            os.makedirs(path)
        except OSError:
            pass

    return open(fpath, *args)


class PregoStreamHandler(logging.StreamHandler):
    pass


def set_logger_default_formatter(logger=None):
    logger = logger or logging.getLogger()
    formatstr = '%(levelcapital)s. %(message)s'
    set_logger_formatter(logger, CapitalLoggingFormatter(formatstr))


def set_logger_formatter(logger, formatter):
    for handler in logger.handlers:
        handler.setFormatter(formatter)


def create_logger(name):
    retval = logging.getLogger(name)
#    retval.setLevel(logging.DEBUG)
    retval.propagate = True
    return retval


class StatusFilter(logging.Filter):
    def __init__(self, item=None):
        self.item = item
        super(StatusFilter, self).__init__()

    def filter(self, record):
        if self.item is None:
            return True

        msg = string.Template(record.msg)
        values = {}
        try:
            values['name'] = self.item.name
            values['status'] = self.item.status.pretty()
        except AttributeError:
            pass

        record.msg = "{0}{1}".format(msg.safe_substitute(values), str(term().normal))
        return True


def update_obj(dst, src):
    for key, value in src.items():
        setattr(dst, key, value)


def load_default_config(dest):
    config = configobj.ConfigObj(configspec=PREGO_SPECS)
    config.validate(validate.Validator())
    update_obj(dest, config['ui'])


def set_testpath():
    def is_test_caller(frame):
        current = "{0.major}.{0.minor}".format(sys.version_info)
        if current in ['3.5', '3.6', '3.7']:
            return frame[3] == 'testMethod()'

        return frame[2] == '_callTestMethod'

    if gvars.testpath is None:
        return

    _next = False
    it = iter(traceback.extract_stack())
    for frame in it:
        if _next:
            gvars.testpath = frame[0]
            return

        if is_test_caller(frame):
            _next = True


def to_text(e):
    try:
        return str(e)
    except UnicodeDecodeError:
        return repr(e)
