from pypidb._exceptions import (
    InvalidPackage,
    InvalidPackageVersion,
    IncompletePackageMetadata,
    PackageWithoutFiles,
    PackageWithoutUrls,
    UnrecognisedStdlibBackport,
)
from tests.utils import _TestBase


class TestVersion(_TestBase):
    def test_rfc6555(self):
        # Current release is 0.0.0
        url = self.converter.get_vcs("rfc6555")
        self.assertInsensitiveEqual(url, "https://github.com/SethMichaelLarson/rfc6555")

    def test_zmq(self):
        with self.assertRaises(InvalidPackageVersion):
            self.converter.get_vcs("zmq")

    def test_skimage(self):
        with self.assertRaises(InvalidPackageVersion):
            self.converter.get_vcs("skimage")

    def test_locust(self):
        with self.assertRaises(InvalidPackageVersion):
            self.converter.get_vcs("locust")


class TestFiles(_TestBase):
    def test_django_myrecaptcha(self):
        # Ignore link to https://bitbucket.org/Kizlum/django-myrecaptcha
        with self.assertRaises(PackageWithoutFiles):
            self.converter.get_vcs("django-myrecaptcha")


class TestExceptions(_TestBase):
    def test_missing_package(self):
        with self.assertRaises(InvalidPackage):
            self.converter.get_vcs("reddit")

    def test_stdlib_version_0_0_0_unittest(self):
        with self.assertRaises(InvalidPackageVersion):
            self.converter.get_vcs("unittest")

    def test_stdlib_Wave(self):
        with self.assertRaises(UnrecognisedStdlibBackport):
            self.converter.get_vcs("wave")

    def test_anaconda(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("anaconda")

    def test_bs4(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("bs4")

    def test_dtopt(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("dtopt")
        # 'svn.colorstudy.com' is in urls, however it is removed because of dns failure

    def test_no_urls_pykerberos(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("pykerberos")

    def test_no_urls_ana(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("ana")

    def test_no_urls_augeas(self):
        with self.assertRaises(InvalidPackage):
            self.converter.get_vcs("augeas")

    def test_no_urls_dbf(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("dbf")

    def test_no_urls_fedorahosted_suds(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("suds")

    def test_no_urls_evtx(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("evtx")

    def test_no_urls_inifile(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("inifile")

    def test_no_urls_kid(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("kid")

    def test_no_urls_kmod(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("kmod")

    def test_no_urls_pygments_ansi_color(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("pygments-ansi-color")

    def test_no_urls_pyjwkest(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("pyjwkest")

    def test_no_urls_axolotl_curve25519(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("python-axolotl-curve25519")

    def test_no_urls_qet_tb_generator(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("qet_tb_generator")

    def test_no_urls_selection(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("selection")

    def test_no_urls_random2(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("random2")

    def test_no_urls_dialog(self):
        with self.assertRaises(PackageWithoutFiles):
            self.converter.get_vcs("dialog")

    def test_no_urls_termcolor(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("termcolor")

    def test_no_urls_strict_rfc3339(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("strict-rfc3339")

    def test_no_urls_Durus(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("Durus")

    def test_no_urls_sane(self):
        with self.assertRaises(PackageWithoutFiles):
            self.converter.get_vcs("sane")

    def test_no_urls_testflo(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("testflo")

    def test_no_urls_moksha(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("moksha-common")
        # Very slow, test_non_found_43, test_non_found_42, test_non_found_39
        # also: test_non_found_81, test_non_found_65
        # cache dns errors?

    def test_no_urls_fedorahosted(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("kitchen")

    def test_no_urls_bencode(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("bencode")

    def test_no_urls_demjson(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("demjson")

    def test_no_urls_kaa(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("kaa-base")

    def test_non_found_pythonpaste_org(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("Tempita")

    def test_python_org_typing_backport(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("typing")

    def test_python_org_url(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("python-docs-theme")

    def test_ovirt_404(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("ovirt-engine-sdk")

    def test_ovirt_v2(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("ovirt-engine-sdk-python")

    def test_no_urls_awsebcli(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("awsebcli")

    def test_github_issues_tools(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("github-issues-tools")

    def test_non_found_BitVector(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("BitVector")
        # https://engineering.purdue.edu/kak/dist/BitVector-3.4.9.html isnt suitable

    def test_non_found_cerealizer(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("cerealizer")
        # requires depth 2 to find https://bitbucket.org/jibalamy/cerealizer

    def test_non_found_pybibframe(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("pybibframe")

    def test_not_found_abclient(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("abclient")

    def test_logentries(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("logentries")

    def test_git_ssh_scheme(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("triforce")
        # ignore 'git+ssh://git@github.com/seveas/git-spindle.git'
        # TODO: add check that it was parsed and excluded

    def test_non_found_mysql(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("mysql-connector-python")

    def test_not_found_whois_1(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("pythonwhois")
        # depth 2 will find https://github.com/joepie91/python-whois

    def test_non_found_pyweblib(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("pyweblib")

    def test_pytidylib(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("pytidylib")

    def test_mailgun(self):
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("mailgun")

    def test_amazon_dax_client(self):
        with self.assertRaises(IncompletePackageMetadata):
            self.converter.get_vcs("amazon-dax-client")

    def test_logilab_aspects(self):
        with self.assertRaises(PackageWithoutFiles):
            self.converter.get_vcs("aspects")
