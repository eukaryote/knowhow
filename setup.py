# coding=utf8

# No future imports here so that unsupported Python versions will get a useful
# error message with version requirements rather than an ImportError.

from os.path import abspath, dirname, join
import sys

from setuptools import setup
from setuptools.command.test import test as testcommand

import knowhow

HERE_DIR = abspath(dirname(__file__))


def check_version():
    version = sys.version_info[:2]
    if version < (2, 7) or (version >= (3, 0) and version < (3, 4)):
        sys.stderr.write("knowhow requires Python 2.7 or Python 3.4+\n")
        sys.exit(1)


def read(*filenames):
    buf = []
    for filename in filenames:
        filepath = join(HERE_DIR, filename)
        try:
            with open(filepath, "r") as f:
                buf.append(f.read())
        except IOError:
            pass  # ignore (running tests under tox)
    return "\n\n".join(buf)


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
    name="knowhow",
    version=knowhow.__version__,
    url="http://github.com/eukaryote/knowhow/",
    license="Apache Software License",
    author="Calvin Smith",
    author_email="sapientdust+knowhow@gmail.com",
    install_requires=["whoosh", "six", "docopt", "pytz"],
    cmdclass={"test": PyTest},
    description=("A simple knowledge repository that is searchable and scriptable"),
    long_description=read("README.rst", "CHANGES.rst"),
    packages=[knowhow.__name__],
    include_package_data=True,
    platforms="any",
    test_suite="tests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Natural Language :: English",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: General",
        "Topic :: Text Processing :: Indexing",
    ],
    extras_require={
        "testing": ["pytest", "mock", "pytest-cov", "pytest-pyflake8"],
        "develop": ["wheel"],
    },
)
