from __future__ import print_function

from setuptools import setup
from setuptools.command.test import test as TestCommand

import os
import sys

import knowhow

here_dir = os.path.abspath(os.path.dirname(__file__))


def read(*filenames):
    buf = []
    for filename in filenames:
        filepath = os.path.join(here_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            buf.append(f.read())
    return '\n\n'.join(buf)

long_description = read('README.md', 'CHANGES.md')


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='knowhow',
    version=knowhow.__version__,
    url='http://github.com/eukaryote/knowhow/',
    license='Apache Software License',
    author='eukaryote',
    tests_require=['pytest'],
    install_requires=[
        'whoosh==2.5.7',
        'six==1.6.1',
        'docopt==0.6.1'
    ],
    cmdclass={'test': PyTest},
    author_email='sapientdust+knowhow@gmail.com',
    description=(
        'A simple knowledge repository that is searchable and scriptable ' +
        'from shells, text editors, window managers, and more'
    ),
    long_description=long_description,
    packages=['knowhow'],
    include_package_data=True,
    platforms='any',
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha'
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Indexing',
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
