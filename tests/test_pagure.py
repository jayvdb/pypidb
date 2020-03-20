from unittest_expander import expand, foreach

from pypidb._pagure import _pagure_io
from tests.utils import _TestBase, web_session

pagure_io = ["copr", "copr-common", "python-daemon", "rustcfg", "wikitcms"]


@expand
class TestPagureIO(_TestBase):
    @foreach(pagure_io)
    def test_package(self, name):
        url = self.converter.get_vcs(name)
        self.assertIsNotNone(url)
        self.assertIn("//pagure.io/", url)
        r = web_session.head(url)
        r.raise_for_status()

    def test_daemon(self):
        url = self.converter.get_vcs("python-daemon")
        self.assertInsensitiveEqual(url, "https://pagure.io/python-daemon")

    def test_daemon_issues(self):
        url = _pagure_io("https://pagure.io/python-daemon/issues")
        self.assertInsensitiveEqual(url, "https://pagure.io/python-daemon")

    def test_invalid(self):
        url = _pagure_io("https://pagure.io/invalid")
        self.assertIsNone(url)

    def test_wikitcms(self):
        url = self.converter.get_vcs("wikitcms")
        self.assertEqual(url, "https://pagure.io/fedora-qa/python-wikitcms")

    def test_meta_repo(self):
        url = _pagure_io("https://pagure.io/fedora-qa/foo/bar")
        self.assertEqual(url, "https://pagure.io/fedora-qa")
