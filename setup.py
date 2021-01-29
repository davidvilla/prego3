#!/usr/bin/python3

# Copyright (C) 2012-2018 David Villa Alises
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from distutils.core import setup
from setuptools import find_packages


def get_reqs():
    with open('requirements.txt') as fd:
        return fd.readlines()


exec(open('version.py').read())

config = dict(
    name             = 'prego3',
    version          = __version__,
    description      = 'System test framework over POSIX shells (python3 version',
    author           = 'David Villa Alises',
    author_email     = 'David.Villa@gmail.com',
    entry_points     = {
        'console_scripts': [ 'prego3=prego:run' ]
    },
    data_files       = [
        ('share/doc/prego3', ['README.rst']),
        ('share/lib/prego3', ['config.spec', 'defaults.config']),
    ],
    url              = 'https://bitbucket.org/arco_group/prego',
    license          = 'GPLv3',
    packages         = find_packages(),
    provides         = ['prego3'],
    long_description = open('README.rst').read(),
    install_requires = get_reqs(),
    classifiers      = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

setup(**config)
