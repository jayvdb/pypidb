import unittest

from pypidb._exceptions import IncompletePackageMetadata, InvalidPackage

from unittest_expander import expand, foreach

from tests.data import bad_metadata, expected, failures
from tests.test_fedora import _fedora_packages
from tests.test_top import _all as _top_all
from tests.utils import _stdlib, _TestBase

try:
    from tests.datasets import get_opensuse_packages, OpenSUSEOBSLoader
except (SyntaxError, ImportError):
    raise unittest.SkipTest("Disabled on Python 2")

repeat_all = True
repeat_expected = True
repeat_failures = True


def _fetch_names(project, ignore_failures=True):
    packages = get_opensuse_packages(project)
    names = []
    for name in packages:
        if name in _stdlib:
            continue

        if not repeat_all and name.lower() in [i.lower() for i in _top_all]:
            continue

        if name.lower() in [i.lower() for i in _fedora_packages]:
            continue

        if not repeat_expected and name.lower() in [i.lower() for i in expected]:
            continue

        if not repeat_failures and name.lower() in [i.lower() for i in bad_metadata]:
            continue

        if (
            not repeat_failures
            and ignore_failures
            and name.lower() in [i.lower() for i in failures]
        ):
            continue

        names.append(name)

    return sorted(names)


@expand
class TestOpenSUSE(_TestBase):
    @foreach(OpenSUSEOBSLoader._not_pypi)
    def test_invalid_name(self, name):
        if name not in ["docs", "pyGRID"]:
            with self.assertRaises(InvalidPackage):
                self._get_scm(name)
        if not name.startswith("python-"):
            with self.assertRaises(InvalidPackage):
                self._get_scm("python-" + name)
        if not name.startswith("py") and name not in ["espeak"]:
            with self.assertRaises(InvalidPackage):
                self._get_scm("py" + name)


@expand
class TestOpenSUSEMain(_TestBase):

    names = _fetch_names(project="devel:languages:python", ignore_failures=False)
    expected_failures = _TestBase.expected_failures + [
        "ana",
        "application",
        "bencode",
        "bindep",
        "bitvector",
        "bobodoctestumentation",
        "bpython",
        "durus",
        "evtx",
        "Gloo",
        "inifile",
        "kid",
        "mysql-connector-python",
        "nagios-http-json",  # deleted
        "ovirt-engine-sdk",
        "project-config",  # invalid package
        "pychart",
        "pyjwkest",
        "pygments-ansi-color",
        "pykerberos",
        "pyprint",
        "python-axolotl-curve25519",
        "python-docs-theme",
        "pythonwhois",
        "pytidylib",
        "qet-tb-generator",
        "selection",
        "strict-rfc3339",
        "testflo",
    ]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSENumeric(_TestBase):

    names = _fetch_names(project="devel:languages:python:numeric")
    expected_failures = [
        "morfessor",
        "pomegranate",
        "pyfeyn",
        "pylineclip",
        "pymol",
        "pyprimes",
        "pyzo",
        "psylab",
    ]

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

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEJupyter(_TestBase):

    names = _fetch_names(project="devel:languages:python:jupyter")
    expected_failures = ["ipympl", "ipysheet", "jupyterlab-pygments"]

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
    expected_failures = ["mailman-web"]

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
        try:
            self._test_names([name], ignore_setuppy=True)
        except IncompletePackageMetadata:
            pass


@expand
class TestOpenSUSEAWS(_TestBase):

    names = _fetch_names("devel:languages:python:aws")

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestOpenSUSEMisc(_TestBase):

    names = _fetch_names(project="devel:languages:python:misc")
    expected_failures = [
        "emencia-django-newsletter",  # missing repo
        "schevo",  # missing repo
        "schevogears",
        "schevosql",
    ]
    _allow_missing = True
    _ignore_invalid = True

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])
