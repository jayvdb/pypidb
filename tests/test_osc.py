import unittest

from unittest_expander import expand, foreach

from tests.data import bad_metadata, expected, failures
from tests.test_fedora import _fedora_packages
from tests.test_top import _all as _top_all
from tests.utils import _stdlib, _TestBase

try:
    from tests.datasets import get_opensuse_packages
except (SyntaxError, ImportError):
    raise unittest.SkipTest("Disabled on Python 2")


def _fetch_names(project, ignore_failures=True):
    packages = get_opensuse_packages(project)
    names = []
    for name in packages:
        if name in _stdlib:
            continue

        if name.lower() in [i.lower() for i in _top_all]:
            continue

        if name.lower() in [i.lower() for i in _fedora_packages]:
            continue

        if name.lower() in [i.lower() for i in expected]:
            continue

        if name.lower() in [i.lower() for i in bad_metadata]:
            continue

        if ignore_failures and name.lower() in [i.lower() for i in failures]:
            continue

        names.append(name)

    return sorted(names)


@expand
class TestOpenSUSEMain(_TestBase):

    names = _fetch_names(project="devel:languages:python", ignore_failures=False)
    expected_failures = _TestBase.expected_failures + [
        "flup",
        "Gloo",
        "nagios-http-json",  # deleted
    ]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSENumeric(_TestBase):

    names = _fetch_names(project="devel:languages:python:numeric")
    expected_failures = ["pylineclip", "pyzo"]  # wrong result  # read timeout

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEPyTest(_TestBase):

    names = _fetch_names(project="devel:languages:python:pytest")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEDjango(_TestBase):

    names = _fetch_names(project="devel:languages:python:django")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEFlask(_TestBase):

    names = _fetch_names(project="devel:languages:python:flask")
    _allow_missing = False

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEJupyter(_TestBase):

    names = _fetch_names(project="devel:languages:python:jupyter")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEAvocado(_TestBase):

    names = _fetch_names(project="devel:languages:python:avocado")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEMailman(_TestBase):

    names = _fetch_names(project="devel:languages:python:mailman")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSECertbot(_TestBase):

    names = _fetch_names(project="devel:languages:python:certbot")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEAzure(_TestBase):

    names = _fetch_names(project="devel:languages:python:azure")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEAWS(_TestBase):

    names = _fetch_names("devel:languages:python:aws")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEMisc(_TestBase):

    names = _fetch_names(project="devel:languages:python:misc")
    _allow_missing = True
    _ignore_invalid = True

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])
