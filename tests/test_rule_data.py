from unittest_expander import expand, foreach

from pypidb._rules import rules
from pypidb._similarity import normalize
from tests.data import bad_metadata
from tests.utils import _TestBase


def _collate_preload():
    packages = []
    for rule in rules.values():
        if rule.preload:
            packages += [i for i in rule.preload if normalize(i) not in rules]

    return sorted(set(packages))


_indirect_preload_names = _collate_preload()
_direct_names = [i.name for i in rules.values()]
_rule_names = _direct_names + _indirect_preload_names


@expand
class TestRuleKey(_TestBase):

    names = _direct_names
    ignore_missing = [
        i.name
        for i in rules.values()
        if normalize(i.name) in [normalize(i) for i in bad_metadata]
    ]

    @foreach(names)
    def test_package(self, name):
        assert normalize(name) == name
        self._test_names([name], ignore_not_found=name in self.ignore_missing)


@expand
class TestRulePreload(_TestBase):

    names = _indirect_preload_names
    expected_failures = ["project-config", "readthedocs-org"]

    @foreach(names)
    def test_package(self, name):
        assert normalize(name) == name
        self._test_names([name])
