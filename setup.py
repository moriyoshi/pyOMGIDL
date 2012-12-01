#!/usr/bin/env python

import os
import sys
from setuptools import setup
from setuptools.dist import Distribution as _Distribution
from setuptools.command.build_py import build_py as _build_py
from setuptools import find_packages
from types import *

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'ply >= 3.0',
    'zope.interface',
    ]

class Distribution(_Distribution):
    def __init__(self, *args, **kwargs):
        self.generation_hooks = []
        _Distribution.__init__(self, *args, **kwargs)

class build_py(_build_py):
    def initialize_options(self):
        _build_py.initialize_options(self)

    def byte_compile(self, *arg, **kwarg):
        self.generate_modules()
        _build_py.byte_compile(self, *arg, **kwarg)

    def generate_modules(self):
        generation_hooks = getattr(self.distribution, 'generation_hooks', None)
        if generation_hooks:
            for hook in generation_hooks:
                hook(self)

def ply_generation_hook(builder):
    old_path = sys.path
    sys.path[0:0] = [builder.build_lib]
    __import__('pyomgidl.reader').reader.initializePLY()
    sys.path=old_path

setup(
    distclass=Distribution,
    cmdclass={ 'build_py': build_py },
    name='pyOMGIDL',
    version="0.0.1",
    description='OMG IDL parser and code generator',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Topic :: Software Development :: Object Brokering :: CORBA",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        ],
    author='pyOMGIDL project',
    author_email='mozo@mozo.jp',
    url='http://github.com/moriyoshi/pyOMGIDL',
    package_dir={'':'src'},
    packages=find_packages('src'),
    include_package_data=True,
    setup_requires=requires,
    install_requires=requires,
    tests_require=requires,
    test_suite='pyomgidl.tests.suite',
    generation_hooks=[
        ply_generation_hook,
        ]
    )
