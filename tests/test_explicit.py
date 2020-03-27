import unittest

from unittest_expander import expand, foreach

from pypidb._compat import PY2
from pypidb._db import _fetch_mapping
from pypidb._github import GitHubAPIMessage, check_repo
from pypidb._pypi import InvalidPackage
from pypidb._similarity import _compute_similarity, normalize
from tests.data import (
    exact,
    exact_fetched,
    exact_metadata,
    invalid,
    mismatch,
    missing_repos,
    name_mismatch_fetched,
    name_mismatch_metadata,
)
from tests.utils import _TestBase, normalise_list, web_session

expected = {}
expected.update(exact)
expected.update(mismatch)

missing_repos = normalise_list(missing_repos)


class _ExplicitBase(object):
    def _check_result(self, name, url):
        pass

    def _test_package(self, name):
        try:
            url = self._get_scm(name)
        except InvalidPackage:
            self.assertIn(name, invalid)
            raise unittest.SkipTest("{} is an invalid package".format(name))
        except unittest.SkipTest:
            raise
        except Exception as e:
            self.assertIn(name, self.expected_failures, e)

        if name in self.expected_failures:
            return
        self.assertIsNotNone(url)
        self.assertNotIn(name, invalid)

        expected = self.expected[name]

        self.assertInsensitiveEqual(url, expected)
        self._check_result(name, url)

        return url


@expand
class TestExactFromJson(_TestBase):

    expected = expected

    def _check_result(self, name, url):
        normalised_name = normalize(name)

        r = None
        if normalised_name in missing_repos:
            pass
        elif url.startswith("https://github.com/"):
            slug = url[len("https://github.com/") :]
            rv = self._check_github_repo(slug)

            self.assertTrue(rv)

            try:
                rv = self._check_github_setuppy(slug, normalised_name)
            except GitHubAPIMessage as e:
                raise unittest.SkipTest(str(e))

            if rv is False:
                return
            self.assertTrue(rv)

        else:
            r = web_session.get(url, allow_redirects=False)

        if r is not None:
            r.raise_for_status()
            self.assertEqual(r.url, url)
            location = r.headers.get("location")
            if location:
                self.assertIn(r.status_code, [301, 302])
                location = location.replace(
                    "code.google.com/archive/p/", "code.google.com/p/"
                )
                self.assertIn(location, [url, url + "/"])
            else:
                self.assertEqual(r.status_code, 200)

    @foreach(exact_metadata.keys())
    def test_package(self, name):
        expected = self.expected[name]

        url = self._get_scm(name)

        self.assertIsNotNone(url)
        self.assertInsensitiveEqual(url, expected)

        normalised_name = normalize(name)
        fetch_list = _fetch_mapping[normalised_name]
        self.assertFalse(fetch_list)

        self._check_result(name, url)

        if PY2:
            return

        if isinstance(expected, str):
            self.assertLess(
                _compute_similarity(name, expected),
                0.05,
                "{} - {} should be moved to name mismatches".format(name, expected),
            )
        else:
            for i in expected:
                self.assertLess(
                    _compute_similarity(name, i),
                    0.05,
                    "{} - {} should be moved to name mismatches".format(name, expected),
                )


@expand
class TestExactFetched(_TestBase):

    expected = expected

    @foreach(exact_fetched.keys())
    def test_package(self, name):
        expected = self.expected[name]

        url = self._get_scm(name)

        self.assertIsNotNone(url)
        self.assertInsensitiveEqual(url, expected)

        normalised_name = normalize(name)
        fetch_list = _fetch_mapping[normalised_name]
        self.assertTrue(fetch_list)

        if normalised_name in missing_repos:
            pass
        elif url.startswith("https://github.com/"):
            slug = url[len("https://github.com/") :]
            rv = self._check_github_repo(slug)

            self.assertTrue(rv)

            try:
                rv = self._check_github_setuppy(slug, normalised_name)
            except GitHubAPIMessage as e:
                raise unittest.SkipTest(str(e))

            if rv is False:
                return
            self.assertTrue(rv)

        else:
            r = web_session.get(url)
            r.raise_for_status()

        if PY2:
            return

        if isinstance(expected, str):
            self.assertLess(
                _compute_similarity(name, expected),
                0.05,
                "{} - {} should be moved to name mismatches".format(name, expected),
            )
        else:
            for i in expected:
                self.assertLess(
                    _compute_similarity(name, i),
                    0.05,
                    "{} - {} should be moved to name mismatches".format(name, expected),
                )


@expand
class TestMismatchFromJson(_TestBase):

    expected = expected
    names = mismatch
    expected_failures = []

    @foreach(name_mismatch_metadata.keys())
    def test_package(self, name):
        expected = self.expected[name]

        try:
            url = self._get_scm(name)
        except unittest.SkipTest:
            raise
        except Exception:
            if name in self.expected_failures:
                return
            raise

        if name in self.expected_failures:
            return

        self.assertIsNotNone(url)
        self.assertInsensitiveEqual(url, expected)
        if isinstance(expected, str):
            self.assertIn("/", expected, "{} should be {}".format(expected, url))

        normalised_name = normalize(name)
        fetch_list = _fetch_mapping[normalised_name]
        self.assertFalse(fetch_list)

        if normalised_name in missing_repos:
            pass
        elif url.startswith("https://github.com/"):
            slug = url[len("https://github.com/") :]
            rv = self._check_github_repo(slug)

            self.assertTrue(rv)

            try:
                rv = self._check_github_setuppy(slug, normalised_name)
            except GitHubAPIMessage as e:
                raise unittest.SkipTest(str(e))

            if rv is False:
                return
            self.assertTrue(rv)

        else:
            r = web_session.get(url)
            r.raise_for_status()

        if PY2:
            return

        if isinstance(expected, str):
            self.assertGreater(_compute_similarity(name, expected), 0.05)
        else:
            highest = 0
            for i in expected:
                val = _compute_similarity(name, i)
                highest = max(highest, val)
            self.assertGreater(highest, 0.05)


@expand
class TestMismatchFetched(_ExplicitBase, _TestBase):

    expected = expected
    names = mismatch
    expected_failures = ["marionette-driver"]

    @foreach(name_mismatch_fetched.keys())
    def test_package(self, name):
        expected = self.expected[name]

        url = self._test_package(name)

        if name in self.expected_failures:
            return

        self.assertIsNotNone(url)
        self.assertInsensitiveEqual(url, expected)
        if isinstance(expected, str):
            self.assertIn("/", expected, "{} should be {}".format(expected, url))

        normalised_name = normalize(name)
        fetch_list = _fetch_mapping[normalised_name]

        self.assertTrue(fetch_list)

        if normalised_name in missing_repos:
            pass
        elif url.startswith("https://github.com/"):
            slug = url[len("https://github.com/") :]
            rv = self._check_github_repo(slug)

            self.assertTrue(rv)

            try:
                rv = self._check_github_setuppy(slug, normalised_name)
            except GitHubAPIMessage as e:
                raise unittest.SkipTest(str(e))

            if rv is False:
                return
            self.assertTrue(rv)

        elif url == "https://wiki.mozilla.org/Auto-tools/Projects/Mozbase":
            # Fetching is a bit slow, and failures for moz* are very repetitive
            pass
        else:
            r = web_session.get(url)
            r.raise_for_status()

        if PY2:
            return

        if isinstance(expected, str):
            self.assertGreater(_compute_similarity(name, expected), 0.05)
        else:
            highest = 0
            for i in expected:
                val = _compute_similarity(name, i)
                highest = max(highest, val)
            self.assertGreater(highest, 0.05)
