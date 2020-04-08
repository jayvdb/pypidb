import unittest

from unittest_expander import expand, foreach

from pypidb._exceptions import InvalidPackage

from tests.data import expected, failures
from tests.test_top import _all as _top_all
from tests.utils import _stdlib, _TestBase

try:
    from tests.datasets import get_fedora_packages, PortingdbLoader
except (SyntaxError, ImportError):
    raise unittest.SkipTest("Disabled on Python 2")

repeat_all = True
repeat_expected = True
repeat_failures = True


def _fetch_names():
    packages = get_fedora_packages()
    names = []
    for name in packages:

        if name in _stdlib:
            continue

        if not repeat_all and name.lower() in [i.lower() for i in _top_all]:
            continue

        if not repeat_expected and name.lower() in [i.lower() for i in expected]:
            continue

        if not repeat_failures and name.lower() in [i.lower() for i in failures]:
            continue

        names.append(name)

    return sorted(names)


_fedora_packages = _fetch_names()


@expand
class TestFedora(_TestBase):

    names = _fedora_packages
    expected_failures = [
        "abclient",
        "ana",
        "anykeystore",
        "augeas",
        "bigsuds",
        "bottle-sqlite",
        "catkin-sphinx",
        "Cerealizer",
        "certifi",
        "coverage_pth",
        "cvxopt",
        "dbf",
        "demjson",
        "dialog",
        "digitalocean",  # version 0
        "dmidecode",
        "dtopt",
        "fiat",
        "geoip",
        "graph-tool",
        "interfile",
        "justbases",
        "keystoneclient",  # version 0
        "kitchen",
        "kmod",
        "marshmallow-enum",
        "moksha.common",
        "moksha.hub",
        "mallard-ducktype",
        "nose-fixes",
        "openoffice",
        "openopt",
        "oslo.sphinx",  # no license
        "petlink",
        "pivy",
        "pyalsa",
        "pybugz",
        "pychess",
        "pycmd",
        "pycpuinfo",
        "pyfim",
        "pykdtree",  # no license
        "pymol",  # no files
        "pyprocdev",
        "pyro",
        "pyrpm",
        "py-spidev",
        "ptrace",
        "python-hglib",
        "python-mpd",
        "python-uinput",
        "pyvirtualize",
        "random2",
        "reportlab",
        "requestsexceptions",
        "script",  # no files
        "simplewrap",
        "suds",
        "tambo",
        "tempita",
        "termcolor",
        "tilestache",  # https://github.com/jayvdb/pypidb/issues/93
        "TroveClient",
        "zbase32",
        "zuul-sphinx",  # no license
    ]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])

    @foreach(PortingdbLoader._not_pypi)
    def test_invalid_name(self, name):
        if name not in ["docs"]:
            with self.assertRaises(InvalidPackage):
                self._get_scm(name)
        if not name.startswith("python-"):
            with self.assertRaises(InvalidPackage):
                self._get_scm("python-" + name)
        if not name.startswith("py") and name not in ["docs", "lxc"]:
            with self.assertRaises(InvalidPackage):
                self._get_scm("py" + name)
        if name.startswith("py") and name not in ["pybox2d", "pyev", "pysvn"]:
            with self.assertRaises(InvalidPackage):
                self._get_scm(name[2:])
