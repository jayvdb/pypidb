from unittest_expander import expand, foreach

from tests.data import exact, mismatch, missing_repos
from tests.utils import _TestBase, normalize, web_session

expected = {}
expected.update(exact)
expected.update(mismatch)


class TestSpecific(_TestBase):
    def test_pylirc(self):
        self.assertRaisesNoUrls("pylirc")
        # "https://sourceforge.net/projects/pylirc"


@expand
class TestExplicit(_TestBase):

    expected = expected
    names = [
        name
        for name, url in expected.items()
        if "sourceforge.net" in url and "sourceforge.net/projects/turbogear1" not in url
    ]
    expected_failures = []

    @foreach(names)
    def test_package(self, name):
        expected = self.expected[name]
        try:
            url = self.converter.get_vcs(name)
        except Exception:
            if name in self.expected_failures:
                return
            raise

        if name in self.expected_failures:
            return

        self.assertIsNotNone(url)
        self.assertInsensitiveEqual(url, expected)

        normalised_name = normalize(name)

        if normalised_name in missing_repos:
            return
        r = web_session.get(url)
        r.raise_for_status()
