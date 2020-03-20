import unittest

from unittest_expander import expand, foreach

from tests.data import expected
from tests.utils import _stdlib, _TestBase


def _fetch_names():
    for name in _stdlib:
        # Already tested in separate class
        if name in expected:
            continue

        yield name


@expand
class TestStdlibNames(_TestBase):

    names = sorted(_fetch_names())
    _ignore_invalid = True
    _allow_missing = True
    expected_failures = [
        "ast",
        "chunk",
        "dis",
        "formatter",
        "mailbox",
        "modulefinder",
        "resource",
        "secrets",
        "token",
        "turtle",
        "wave",
        # has url
        "numbers",
        "parser",
        "select",
        "shelve",
        "signal",
        # 'time' has no urls or artifacts
        "trace",
    ]
    # numbers and calendar and trace and signal and shelve and select and parser have urls
    #   calendar republished to https://pypi.org/project/python-calendrical/
    # numbers, select and signal point to github repos which are 404
    #   select was renamed to https://github.com/Jaymon/que
    # time has no urls or artifacts
    # trace links to http://billionuploads.com/ka79h2t4jpi1 which looks dodgy but is 404 atm

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestFailedStdlibNames(_TestBase):

    expected_failures = []

    @foreach(TestStdlibNames.expected_failures)
    @unittest.expectedFailure
    def test_package(self, name):
        self._test_names([name])
