from unittest_expander import expand, foreach

from tests.data import exact, mismatch, missing_repos
from tests.utils import _TestBase, normalize, web_session

expected = {}
expected.update(exact)
expected.update(mismatch)


class TestSpecific(_TestBase):
    def test_odslib(self):
        url = self.converter.get_vcs("odslib")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/angry_elf/odslib")

    def test_pytest_gae(self):
        url = self.converter.get_vcs("pytest-gae")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/petraszd/pytest_gae")

    def test_hachoir_core(self):
        # https://bitbucket.org/haypo has been deleted
        url = self.converter.get_vcs("hachoir-core")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/haypo/hachoir")

    def test_hachoir_metadata(self):
        url = self.converter.get_vcs("hachoir-metadata")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/haypo/hachoir")

    def test_hachoir_parser(self):
        url = self.converter.get_vcs("hachoir-parser")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/haypo/hachoir")


@expand
class TestExplicit(_TestBase):

    expected = expected
    names = [name for name, url in expected.items() if "bitbucket.org" in url]
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
