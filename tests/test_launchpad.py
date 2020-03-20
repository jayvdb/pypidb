from unittest_expander import expand, foreach

from pypidb._lp import _launchpad
from tests.data import exact, mismatch, missing_repos
from tests.utils import _TestBase, normalize, web_session

expected = {}
expected.update(exact)
expected.update(mismatch)


class TestLP(_TestBase):
    def test_pythonxy_archive(self):
        url = "https://code.launchpad.net/~pythonxy/+archive/pythonxy-devel"
        rv = _launchpad(url)
        self.assertEqual(rv, url.replace("code.", ""))

    def test_scm_bzr(self):
        url = self.converter.get_vcs("bzr")
        self.assertEqual(url, "https://launchpad.net/bzr")

    def test_BeautifulSoup(self):
        url = self.converter.get_vcs("BeautifulSoup")
        self.assertEqual(url, "https://launchpad.net/beautifulsoup")

    def test_beautifulsoup4(self):
        url = self.converter.get_vcs("beautifulsoup4")
        self.assertEqual(url, "https://launchpad.net/beautifulsoup")

    def test_testscenarios(self):
        url = self.converter.get_vcs("testscenarios")
        self.assertInsensitiveEqual(url, "https://launchpad.net/testscenarios")

    def test_testrepository(self):
        url = self.converter.get_vcs("testrepository")
        self.assertInsensitiveEqual(url, "https://launchpad.net/testrepository")
        # Also https://github.com/testing-cabal/testrepository

    def test_PyDispatcher(self):
        url = self.converter.get_vcs("PyDispatcher")
        self.assertInsensitiveEqual(
            url, "https://sourceforge.net/projects/pydispatcher"
        )
        # TODO: lower sf.net priority so answer is 'https://launchpad.net/pydispatcher

    def test_versiontools(self):
        url = self.converter.get_vcs("versiontools")
        self.assertInsensitiveEqual(url, "https://launchpad.net/versiontools")
        # TODO: should be enhanced to find https://github.com/zyga/versiontools which is
        # mentioned on https://code.launchpad.net/versiontools

    def test_jsonlib(self):
        url = self.converter.get_vcs("jsonlib-python3")
        self.assertInsensitiveEqual(url, "https://launchpad.net/jsonlib")

    def test_Parsley(self):
        url = self.converter.get_vcs("Parsley")
        self.assertInsensitiveEqual(url, "https://launchpad.net/parsley")

    def test_dkimpy(self):
        url = self.converter.get_vcs("dkimpy")
        self.assertInsensitiveEqual(url, "https://launchpad.net/dkimpy")

    def test_lazr_config(self):
        url = self.converter.get_vcs("lazr.config")
        self.assertInsensitiveEqual(url, "https://launchpad.net/lazr.config")

    def test_pkginfo(self):
        url = self.converter.get_vcs("pkginfo")
        self.assertInsensitiveEqual(url, "https://launchpad.net/pkginfo")

    def test_pyliblzma(self):
        url = self.converter.get_vcs("pyliblzma")
        self.assertInsensitiveEqual(url, "https://launchpad.net/pyliblzma")

    def test_wadllib(self):
        url = self.converter.get_vcs("wadllib")
        self.assertInsensitiveEqual(url, "https://launchpad.net/wadllib")

    def test_subunit(self):
        url = self.converter.get_vcs("python-subunit")
        self.assertInsensitiveEqual(url, "https://launchpad.net/subunit")

    def test_objgraph(self):
        url = self.converter.get_vcs("objgraph")
        self.assertEqual(url, "https://github.com/mgedmin/objgraph")

    def test_repoze_who(self):
        url = self.converter.get_vcs("repoze.who")
        self.assertInsensitiveEqual(url, "https://github.com/repoze/repoze.who")

    def test_zc_buildout(self):
        url = self.converter.get_vcs("zc.buildout")
        self.assertEqual(url, "https://github.com/buildout/buildout")

    def test_zc_recipe_egg(self):
        url = self.converter.get_vcs("zc.recipe.egg")
        self.assertEqual(url, "https://github.com/buildout/buildout")


@expand
class TestExplicit(_TestBase):

    expected = expected
    names = [name for name, url in expected.items() if "launchpad.net" in url]
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
