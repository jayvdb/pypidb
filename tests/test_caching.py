import unittest

import requests
from cachecontrol import CacheControl, CacheController
from cachecontrol.cache import DictCache
from cachecontrol.heuristics import OneDayCache
from pytest_blockage import block_http, httplib
from requests.packages.urllib3.util.timeout import Timeout

from pypidb._adapters import HTTPSAdapter, IPBlockAdapter
from pypidb._db import mappings
from pypidb._pypi import Converter, InvalidPackage
from tests.utils import _TestBase

http_blocked = hasattr(httplib.HTTPConnection.__init__, "blockage")


# TODO: disable if pytest-blockage enabled globally
# add test that MockHttpCall is raised
class TestPyPiJsonCache(_TestBase):
    def test_miss(self):
        if http_blocked:
            return

        converter = Converter(website_timeout=5)

        with self.assertRaises(InvalidPackage):
            converter.get_vcs("doesntexist")

        try:
            with self.assertRaises(InvalidPackage):
                block_http([])

                converter = Converter(website_timeout=5)
                converter.get_vcs("doesntexist")
        finally:
            httplib.HTTPConnection.__init__ = httplib.HTTPConnection.old

    def test_hit(self):
        if http_blocked:
            return

        converter = Converter(website_timeout=5)
        url = converter.get_vcs("simplejson")
        self.assertEqual(url, "https://github.com/simplejson/simplejson")

        del mappings["simplejson"]

        try:
            block_http([])
            converter = Converter(website_timeout=5)
            url = converter.get_vcs("simplejson")
            self.assertEqual(url, "https://github.com/simplejson/simplejson")
        finally:
            httplib.HTTPConnection.__init__ = httplib.HTTPConnection.old

        try:
            del mappings["simplejson"]
        except KeyError:
            pass

    def test_redirect(self):
        if http_blocked:
            return

        # see also https://github.com/ionrock/cachecontrol/issues/214
        converter = Converter(website_timeout=5)
        url = converter.get_vcs("setuptools_scm")
        self.assertEqual(url, "https://github.com/pypa/setuptools_scm")

        del mappings["setuptools-scm"]

        try:
            block_http([])
            converter = Converter(website_timeout=5)
            url = converter.get_vcs("setuptools_scm")
            self.assertEqual(url, "https://github.com/pypa/setuptools_scm")
        finally:
            httplib.HTTPConnection.__init__ = httplib.HTTPConnection.old

        try:
            del mappings["setuptools-scm"]
        except KeyError:
            pass


class TestFakeRedirect(unittest.TestCase):
    def test_redirect_https(self):
        url = "http://httpbin.org/get?foo"
        session = requests.Session()
        session.mount(url, HTTPSAdapter())
        r = session.get(url)
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertNotIn("location", r.headers)

    def test_redirect_https_south(self):
        url = "http://south.aeracode.org/"
        session = requests.Session()
        session.mount(url, HTTPSAdapter())
        r = session.get(url)
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertNotIn("location", r.headers)
        self.assertIn("bitbucket.org", r.text)

    def test_redirect_https_gustavonarea(self):
        url = "http://code.gustavonarea.net/repoze.who.plugins.sa/"
        session = requests.Session()
        session.mount(url, HTTPSAdapter())
        r = session.get(url)
        self.assertEqual(r.url, url.replace("http://", "https://"))
        self.assertNotIn("location", r.headers)
        self.assertIn("github.com", r.text)

    def _test_no_redirect_https_IP(self):
        url = "http://127.0.0.1/repoze.who.plugins.sa/"
        session = requests.Session()
        session.mount(url, HTTPSAdapter())
        r = session.get(url)
        self.assertEqual(r.url, url)
        self.assertNotEqual(r.url, url.replace("http://", "https://"))

    def test_block_ip(self):
        url = "http://127.0.0.1/repoze.who.plugins.sa/"
        session = requests.Session()
        session.mount("http://", IPBlockAdapter())
        r = session.get(url)
        self.assertEqual(r.status_code, 500)
        self.assertEqual(r.url, url)

    def _test_timeout_moksha_requests_session(self):
        url = "https://mokshaproject.net"
        session = requests.Session()
        r = session.get(url, timeout=Timeout(5))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.url, url)

    def _test_timeout_moksha_requests_get(self):
        url = "https://mokshaproject.net"
        r = requests.get(url, timeout=Timeout(5))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.url, url)

    def _test_timeout_moksha(self):
        # mokshaproject.net is a parked domain
        url = "https://mokshaproject.net"
        from pypidb._cache import get_file_cache_session

        s = get_file_cache_session("web")
        with self.assertRaises(requests.exceptions.ConnectTimeout):
            s.get(url, timeout=Timeout(5))

    def _test_fetch_ply_requests_session(self):
        url = "https://www.dabeaz.com/ply/"

        s = requests.Session()
        r = s.get(url, timeout=Timeout(5))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.url, url)

    def _test_fetch_ply_requests_get(self):
        url = "https://www.dabeaz.com/ply/"

        r = requests.get(url, timeout=Timeout(5))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.url, url)

    def test_fetch_ply_https(self):
        from pypidb._cache import get_file_cache_session

        url = "https://www.dabeaz.com/ply/"

        s = get_file_cache_session("web")
        r = s.get(url, timeout=Timeout(5))
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(r.url, url)
        self.assertEqual(r.url, url.replace("https://", "http://"))

    def test_head_requests_get(self):
        url = "http://gpodder.org/"

        r = requests.head(url, timeout=Timeout(15))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, url)
        self.assertEqual(r.headers["location"], "https://gpodder.github.io")
        self.assertFalse(r.content)

    def _test_head_cachecontrol(self):
        # cache polluted by HEAD
        url = "http://gpodder.org/"

        class MoreCodesCacheController(CacheController):
            def __init__(self, *args, **kwargs):
                kwargs["status_codes"] = (200, 203, 300, 301, 302, 404)
                super(MoreCodesCacheController, self).__init__(*args, **kwargs)

        cache = DictCache()
        s = CacheControl(
            requests.Session(),
            cache=cache,
            heuristic=OneDayCache(),
            cacheable_methods=["GET", "HEAD"],
            controller_class=MoreCodesCacheController,
        )
        r = s.head(url, timeout=Timeout(15))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, url)
        self.assertEqual(r.headers["location"], "https://gpodder.github.io")
        self.assertFalse(r.content)
        self.assertFalse(r.from_cache)

        r = s.get(url, timeout=Timeout(15), allow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, url)
        self.assertEqual(r.headers["location"], "https://gpodder.github.io")
        self.assertTrue(r.content)
        self.assertIn(b"302 Found", r.content)
        self.assertFalse(r.from_cache)

        # Re-fetch the redirect from the cache
        r = s.get(url, timeout=Timeout(15), allow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, url)
        self.assertEqual(r.headers["location"], "https://gpodder.github.io")
        self.assertTrue(r.content)
        self.assertIn(b"302 Found", r.content)

        self.assertTrue(r.from_cache)

        # Now allow redirects

        r = s.get(url, timeout=Timeout(15))
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(r.url, url)
        self.assertTrue(r.content)
        self.assertFalse(r.from_cache)

        # Re-fetch the redirect from the cache
        r = s.get(url, timeout=Timeout(15), allow_redirects=False)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, url)
        self.assertEqual(r.headers["location"], "https://gpodder.github.io")
        self.assertTrue(r.content)
        self.assertIn(b"302 Found", r.content)

        self.assertTrue(r.from_cache)

        # Re-fetch the head from the cache
        r = s.head(url, timeout=Timeout(15))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, url)
        self.assertEqual(r.headers["location"], "https://gpodder.github.io")
        self.assertTrue(r.content)
        self.assertIn(b"302 Found", r.content)
        self.assertTrue(r.from_cache)

    def _test_head_302_bypasses_cache(self):
        # HEAD 302 is completed before the caching
        from pypidb._cache import get_file_cache_session

        url = "http://gpodder.org/"

        s = get_file_cache_session("web")
        r = s.head(url, timeout=Timeout(15))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, url)
        self.assertEqual(r.headers["location"], "https://gpodder.github.io")
        self.assertFalse(r.content)
        self.assertFalse(hasattr(r, "from_cache"))

        r = s.head(url, timeout=Timeout(15))
        self.assertFalse(hasattr(r, "from_cache"))

    def test_vlc(self):
        from pypidb._cache import get_file_cache_session

        url = "https://wiki.videolan.org/PythonBinding"

        s = get_file_cache_session("web")
        r = s.get(url, timeout=Timeout(15))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.url, url)
        self.assertTrue(r.content)
        self.assertIn(b'<meta name="generator" content="MediaWiki', r.content)
        self.assertIn(b"https://git.videolan.org/", r.content)
