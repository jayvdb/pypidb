from requests.exceptions import TooManyRedirects
from unittest_expander import expand, foreach

from pypidb._cache import get_file_cache
from pypidb._pypi import IncompletePackageMetadata, InvalidPackage, PackageWithoutUrls
from pypidb._similarity import _compute_similarity
from tests.data import (
    bad_metadata,
    missing_repos,
    setuppy_mismatches,
    sometimes_wrong_result,
    wrong_result,
)
from tests.test_rule_data import _rule_names
from tests.utils import _TestBase

web_session = get_file_cache("web")

failures = bad_metadata + sometimes_wrong_result + wrong_result + missing_repos

bad_metadata = [i for i in bad_metadata if i not in _rule_names]


@expand
class TestPyPiBadMetadata(_TestBase):
    @foreach(bad_metadata)
    def test_package(self, name):
        self.assertNotIn(name, wrong_result)
        self.assertNotIn(name, sometimes_wrong_result)
        self.assertNotIn(name, missing_repos)

        try:
            url = self._get_scm(name)
        except (InvalidPackage, IncompletePackageMetadata, PackageWithoutUrls):
            if self._debug_no_urls:
                self.assertTrue(False)
            url = None
        except TooManyRedirects:
            if self._debug_no_urls:
                self.assertTrue(False)
            url = None
        if self._debug_no_urls:
            self.assertIsNotNone(url)
        else:
            self.assertIsNone(url)


@expand
class TestWrong(_TestBase):
    @foreach(wrong_result)
    def test_package(self, name):
        self.assertNotIn(name, bad_metadata)
        self.assertNotIn(name, sometimes_wrong_result)
        self.assertNotIn(name, missing_repos)

        url = self._get_scm(name)
        self.assertIsNotNone(url)

        r = web_session.get(url, timeout=20)
        if r.status_code == 404:
            return
        r.raise_for_status()

        distance = _compute_similarity(name, url)
        self.assertGreater(
            distance, 0.13, "{} is a close match to {}".format(url, name)
        )


@expand
class TestWrongSometimes(_TestBase):
    @foreach(sometimes_wrong_result)
    def test_package(self, name):
        self.assertNotIn(name, bad_metadata)
        self.assertNotIn(name, wrong_result)
        self.assertNotIn(name, missing_repos)

        url = self._get_scm(name)
        if not url:
            return

        r = web_session.get(url, timeout=20)
        if r.status_code == 404:
            return
        r.raise_for_status()


@expand
class TestMissingRepo(_TestBase):
    @foreach(missing_repos)
    def test_package(self, name):
        self.assertNotIn(name, bad_metadata)
        self.assertNotIn(name, wrong_result)
        self.assertNotIn(name, sometimes_wrong_result)

        url = self._get_scm(name)
        self.assertIsNotNone(url)

        try:
            r = web_session.head(url, timeout=20)
        except Exception:
            return

        if r.status_code == 405 and "code.google.com" in url:
            r = web_session.get(url, timeout=20)
        try:
            r.raise_for_status()
        except Exception:
            pass
        else:
            if name in ["pychart"]:
                return
            self.assertTrue(False, "{} is not missing for {}".format(url, name))


@expand
class TestSetuppyMismatch(_TestBase):
    @foreach([i.strip("$") for i in setuppy_mismatches if not i.endswith("-")])
    def test_package(self, name):
        self.assertNotIn(name, bad_metadata)
        self.assertNotIn(name, wrong_result)
        self.assertNotIn(name, sometimes_wrong_result)
        self.assertNotIn(name, missing_repos)
        url = self._get_scm(name)
        self.assertIsNotNone(url)
