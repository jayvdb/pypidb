import unittest

from unittest_expander import expand, foreach

from tests.data import expected, failures
from tests.test_top import _all as _top_all
from tests.utils import _stdlib, _TestBase

try:
    from tests.datasets import get_fedora_packages
except (SyntaxError, ImportError):
    raise unittest.SkipTest("Disabled on Python 2")

repeat_expected = False


def _fetch_names():
    packages = get_fedora_packages()
    names = []
    for name in packages:

        if name in _stdlib:
            continue

        if name.lower() in [i.lower() for i in _top_all]:
            continue

        if not repeat_expected and name.lower() in [i.lower() for i in expected]:
            continue

        if name.lower() in [i.lower() for i in failures]:
            continue

        names.append(name)

    return sorted(names)


_fedora_packages = _fetch_names()


@expand
class TestFedora(_TestBase):

    names = _fedora_packages
    expected_failures = ["nose-fixes"]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])
