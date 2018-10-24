# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import filecmp

from commodity.type_ import checked_type
from commodity.str_ import Printable

from .tools import file_types
from .tools import Interpolator


class DeferredItem(object):
    def __init__(self):
        self.task = None

    def config(self, task):
        self.task = task


class DeferredAttr(DeferredItem):
    "An object attribute delegated for late binding"

    def __init__(self, obj, name, attr):
        self.obj = obj
        self.name = name
        self.attr = attr

    def resolve(self):
        return getattr(self.obj, self.attr)

    def __str__(self):
        return 'deferred %s.%s' % (self.obj.__class__.__name__, self.name)


class DeferredContent(DeferredItem):
    def __init__(self, fd):
        super(DeferredContent, self).__init__()
        self.fd = fd

    def resolve(self):
        try:
            return self.fd.read()
        except IOError:
            return None

    def __str__(self):
        return "{0} has".format(self.fd)


class File(Printable):
    def __init__(self, path, fd=None):
        self.path = Interpolator().apply(checked_type(str, path))
        self.fd = fd

    def __eq__(self, other):
        return filecmp.cmp(self.path, other.path)

    @classmethod
    def from_fd(cls, fd):
        "Creates prego.File from standard python file descriptor"
        fd = checked_type(file_types, fd)
        assert not fd.closed, fd
        return File(fd.name, fd)

    def read(self):
        with open(self.path) as fd:
            return fd.read()

    def readline(self):
        with open(self.path) as fd:
            return fd.readline()

    def write(self, data):
        self._assure_open()
        self.fd.write(data)

    def flush(self):
        self._assure_open()
        self.fd.flush()

    @property
    def closed(self):
        return self.fd.closed

    def close(self):
        assert not self.fd.closed
        self.fd.close()

    def _assure_open(self):
        if self.fd is None:
            self.fd = file(self.path, 'w', 0)

        if self.fd.closed:
            raise ValueError('%s was closed' % self.fd.name)

    def find(self, substring):
        raise TypeError("use 'content' attribute to refer file content")

    def exists(self):
        return os.path.exists(self.path)

    def remove(self):
        if self.exists():
            os.remove(self.path)

    @property
    def content(self):
        return DeferredContent(self)

    def __str__(self):
        return "File {0!r}".format(self.path)
