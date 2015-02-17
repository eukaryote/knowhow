# No future imports here so that unsupported Python versions will get a useful
# error message with version requirements rather than an ImportError.

from setuptools import setup
from setuptools.command.test import test as testcommand

from os.path import abspath, dirname, join
import sys

import knowhow

if sys.version_info < (2, 7):
    sys.stdout.write("knowhow requires Python 2.7 or greater\n")
    sys.exit(1)

# PY2 = sys.version_info < (3,)
here_dir = abspath(dirname(__file__))


def read(*filenames):
    buf = []
    for filename in filenames:
        filepath = join(here_dir, filename)
        with open(filepath, 'r') as f:
            buf.append(f.read())
    return '\n\n'.join(buf)


class PyTest(testcommand):

    def finalize_options(self):
        testcommand.finalize_options(self)
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
    author='Calvin Smith',
    author_email='sapientdust+knowhow@gmail.com',
    tests_require=['pytest'],
    install_requires=[
        'whoosh==2.5.7',
        'six==1.9.0',
        'docopt==0.6.2',
        'pytz==2014.10'
    ],
    cmdclass={'test': PyTest},
    description=(
        'A simple knowledge repository that is searchable and scriptable'
    ),
    long_description=read('README.md', 'CHANGES.md'),
    packages=['knowhow'],
    include_package_data=True,
    platforms='any',
    test_suite='tests',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha'
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
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
        'develop': ['wheel'],
    }
)
