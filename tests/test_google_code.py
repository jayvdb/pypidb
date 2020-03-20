from unittest_expander import expand, foreach

from tests.data import exact, mismatch, missing_repos
from tests.utils import _TestBase, normalize, web_session

expected = {}
expected.update(exact)
expected.update(mismatch)


class TestSpecific(_TestBase):
    def test_pydpi(self):
        url = self.converter.get_vcs("pydpi")
        self.assertEqual(url, "https://code.google.com/p/pydpi")

    def test_gmpy(self):
        url = self.converter.get_vcs("gmpy")
        self.assertEqual(url, "https://code.google.com/p/gmpy")

    def test_dicompyler(self):
        url = self.converter.get_vcs("dicompyler")
        self.assertEqual(url, "https://code.google.com/p/dicompyler")

    def test_socksipy_branch(self):
        url = self.converter.get_vcs("socksipy-branch")
        self.assertEqual(url, "https://code.google.com/p/socksipy-branch")

    def test_pyp(self):
        url = self.converter.get_vcs("pyp")
        self.assertEqual(url, "https://code.google.com/p/pyp")

    def test_pyopt(self):
        url = self.converter.get_vcs("pyopt")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/pyopt")

    def test_euclid(self):
        url = self.converter.get_vcs("euclid")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/pyeuclid")

    def test_crc16(self):
        url = self.converter.get_vcs("crc16")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/pycrc16")
        # TODO: should be https://github.com/gennady/pycrc16

    def test_nosetty(self):
        url = self.converter.get_vcs("nosetty")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/nosetty")

    def test_pysvg(self):
        url = self.converter.get_vcs("pysvg")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/pysvg")

    def test_lepl(self):
        url = self.converter.get_vcs("lepl")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/lepl")

    def test_nmap(self):
        url = self.converter.get_vcs("python-nmap")
        # Read meta redirect to go to https://bitbucket.org/xael/python-nmap
        self.assertInsensitiveEqual(url, "https://code.google.com/p/python-nmap")

    def test_fixture(self):
        url = self.converter.get_vcs("fixture")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/fixture")

    def test_leveldb(self):
        url = self.converter.get_vcs("leveldb")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/py-leveldb")

    def test_ntplib(self):
        url = self.converter.get_vcs("ntplib")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/ntplib")

    def test_pysmell(self):
        url = self.converter.get_vcs("pysmell")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/pysmell")

    def test_publicsuffix(self):
        url = self.converter.get_vcs("publicsuffix")
        self.assertInsensitiveEqual(
            url, "https://code.google.com/p/python-public-suffix-list"
        )

    def test_prettytable(self):
        url = self.converter.get_vcs("prettytable")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/prettytable")

    def test_mglob(self):
        url = self.converter.get_vcs("mglob")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/vvtools")

    def test_apache_extras_cpl(self):
        url = self.converter.get_vcs("cql")
        self.assertInsensitiveEqual(
            url, "https://code.google.com/a/apache-extras.org/p/cassandra-dbapi2"
        )

    def test_gdist(self):
        url = self.converter.get_vcs("gdist")
        self.assertNotEqual(url, "https://github.com/the-virtual-brain/tvb-geodesic")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/geodesic")

    def test_django_pagination(self):
        url = self.converter.get_vcs("django-pagination")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/django-pagination")

    def test_django_gravatar(self):
        url = self.converter.get_vcs("django-gravatar")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/django-gravatar")

    def test_django_swaps(self):
        url = self.converter.get_vcs("django-swaps")
        self.assertInsensitiveEqual(url, "https://code.google.com/p/django-swaps")


class TestRedirectOther(_TestBase):
    def test_mox3(self):
        url = self.converter.get_vcs("mox3")
        self.assertInsensitiveEqual(url, "https://opendev.org/openstack/mox3")

    def test_slixmpp(self):
        url = self.converter.get_vcs("slixmpp")
        self.assertInsensitiveEqual(url, "https://lab.louiz.org/poezio/slixmpp")


class TestRedirectGitHub(_TestBase):
    def test_dpkt(self):
        url = self.converter.get_vcs("dpkt")
        self.assertInsensitiveEqual(url, "https://github.com/kbandla/dpkt")

    def test_beatbox(self):
        url = self.converter.get_vcs("beatbox")
        self.assertInsensitiveEqual(url, "https://github.com/superfell/Beatbox")

    def test_pydot2(self):
        url = self.converter.get_vcs("pydot2")
        self.assertInsensitiveEqual(url, "https://github.com/erocarrera/pydot")

    def test_pymilter(self):
        url = self.converter.get_vcs("pymilter")
        self.assertEqual(url, "https://github.com/sdgathman/pymilter")

    def test_cppclean(self):
        url = self.converter.get_vcs("cppclean")
        self.assertInsensitiveEqual(url, "https://github.com/myint/cppclean")

    def test_ply(self):
        url = self.converter.get_vcs("ply")
        self.assertInsensitiveEqual(url, "https://github.com/dabeaz/ply")

    def test_pydot(self):
        url = self.converter.get_vcs("pydot")
        self.assertInsensitiveEqual(url, "https://github.com/pydot/pydot")

    def test_protorpc(self):
        url = self.converter.get_vcs("protorpc")
        self.assertInsensitiveEqual(url, "https://github.com/google/protorpc")

    def test_ibmdb(self):
        url = self.converter.get_vcs("ibm-db")
        self.assertInsensitiveEqual(url, "https://github.com/ibmdb/python-ibmdb")

    def test_ibmdbsa(self):
        url = self.converter.get_vcs("ibm-db-sa")
        self.assertInsensitiveEqual(url, "https://github.com/ibmdb/python-ibmdb")

    def test_scikits_sparse(self):
        url = self.converter.get_vcs("scikits-sparse")
        self.assertInsensitiveEqual(
            url, "https://github.com/scikit-sparse/scikit-sparse"
        )

    def test_pysphere(self):
        url = self.converter.get_vcs("pysphere")
        self.assertInsensitiveEqual(url, "https://github.com/argos83/pysphere")

    def test_cronwatch(self):
        url = self.converter.get_vcs("cronwatch")
        self.assertInsensitiveEqual(url, "https://github.com/wdlowry/cronwatch")

    def test_murmurhash3(self):
        url = self.converter.get_vcs("murmurhash3")
        self.assertInsensitiveEqual(url, "https://github.com/veegee/mmh3")

    def test_iniparse(self):
        url = self.converter.get_vcs("iniparse")
        self.assertInsensitiveEqual(url, "https://github.com/candlepin/python-iniparse")

    def test_progressbar(self):
        url = self.converter.get_vcs("progressbar")
        self.assertInsensitiveEqual(
            url, "https://github.com/niltonvolpato/python-progressbar"
        )

    def test_yara(self):
        url = self.converter.get_vcs("yara")
        self.assertInsensitiveEqual(url, "https://github.com/mjdorma/yara-ctypes")

    def test_webapp(self):
        url = self.converter.get_vcs("webapp")
        self.assertInsensitiveEqual(url, "https://github.com/alectramell/webapp")

    def test_webapp2(self):
        url = self.converter.get_vcs("webapp2")
        self.assertInsensitiveEqual(
            url, "https://github.com/googlecloudplatform/webapp2"
        )

    def test_tvb_gdist(self):
        url = self.converter.get_vcs("tvb-gdist")
        self.assertInsensitiveEqual(
            url, "https://github.com/the-virtual-brain/tvb-geodesic"
        )

    def test_mpmath(self):
        url = self.converter.get_vcs("mpmath")
        self.assertInsensitiveEqual(url, "https://github.com/fredrik-johansson/mpmath")

    def test_scitools(self):
        url = self.converter.get_vcs("SciTools")
        self.assertInsensitiveEqual(url, "https://github.com/hplgit/scitools")

    def test_django_jython(self):
        url = self.converter.get_vcs("django-jython")
        self.assertInsensitiveEqual(
            url, "https://github.com/beachmachine/django-jython"
        )


@expand
class TestExplicit(_TestBase):

    expected = expected
    names = [name for name, url in expected.items() if "code.google.com" in url]
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
