import unittest

from pypidb._rtd import AuthenticationError, ReadtheDocs, get_repo
from tests.utils import _TestBase


class TestGitHubRepo(_TestBase):
    def test_moneta(self):
        rv = get_repo("moneta")
        self.assertEqual(rv, "https://github.com/d9pouces/Moneta")

        url = get_repo("https://moneta.readthedocs.io/")
        self.assertEqual(url, "https://github.com/d9pouces/Moneta")

        url = get_repo("https://moneta.readthedocs.org/")
        self.assertEqual(url, "https://github.com/d9pouces/Moneta")

        url = get_repo("http://moneta.readthedocs.io/")
        self.assertEqual(url, "https://github.com/d9pouces/Moneta")

        url = get_repo("http://moneta.readthedocs.org/")
        self.assertEqual(url, "https://github.com/d9pouces/Moneta")

    def test_http_upgrade_cvxopt(self):
        url = get_repo("cvxopt")
        self.assertEqual(url, "https://github.com/cvxopt/cvxopt")

    def test_uwsgi_docs(self):
        url = get_repo("uwsgi-docs")
        self.assertInsensitiveEqual(url, "https://github.com/unbit/uwsgi")

    def test_mailgun(self):
        url = get_repo("mailgun")
        self.assertInsensitiveEqual(url, "https://github.com/Bogardo/Mailgun")

    def test_simplekml(self):
        url = get_repo("simplekml")
        self.assertInsensitiveEqual(url, "https://github.com/eisoldt/simplekml")

    def test_mailgun_docs(self):
        try:
            url = ReadtheDocs().get_project("mg-documentation")
            self.assertInsensitiveEqual(
                url, "https://github.com/mailgun/documentation.git"
            )
        except AuthenticationError:
            pass

        url = get_repo("mg-documentation")
        self.assertInsensitiveEqual(url, "https://github.com/mailgun/documentation")

    def test_jsonschema_objects(self):
        url = get_repo("python-jsonschema-objects")
        self.assertEqual(url, "https://github.com/cwacek/python-jsonschema-objects")

        url = self.converter.get_vcs("python-jsonschema-objects")
        self.assertEqual(url, "https://github.com/cwacek/python-jsonschema-objects")

    def test_mwlib(self):
        url = get_repo("mwlib")
        self.assertEqual(url, "https://github.com/pediapress/mwlib")

    def test_tidy(self):
        url = get_repo("tidy")
        self.assertEqual(url, "https://github.com/xywei/tidy")

    def test_ccdproc(self):
        url = get_repo("ccdproc")
        self.assertEqual(url, "https://github.com/astropy/ccdproc")

    def test_pygobject(self):
        url = get_repo("pygobject")
        self.assertIsNone(url)


class TestRedirect(_TestBase):
    def test_sqlalchemy(self):
        try:
            url = ReadtheDocs().get_project("sqlalchemy")
        except AuthenticationError:
            raise unittest.SkipTest("auth failure prevents test logic")

        self.assertInsensitiveEqual(
            url, "https://github.com/zzzeek/redirectthedocs.git"
        )

    def test_sqlalchemy_ignored(self):
        url = get_repo("sqlalchemy")
        self.assertIsNone(url)


class TestReadthedocsHosted(_TestBase):
    def test_datarobot(self):
        url = get_repo(
            "https://datarobot-public-api-client.readthedocs-hosted.com/",
            version="v2.19.0",
        )
        self.assertInsensitiveEqual(
            url, "https://github.com/datarobot/public_api_client"
        )

        url = get_repo("https://datarobot-public-api-client.readthedocs-hosted.com/")
        self.assertIsNone(url)

        url = get_repo(
            "https://datarobot-public-api-client.readthedocs-hosted.com/en/v2.19.0/"
        )
        self.assertInsensitiveEqual(
            url, "https://github.com/datarobot/public_api_client"
        )

        url = self.converter.get_vcs("datarobot")
        self.assertInsensitiveEqual(
            url, "https://github.com/datarobot/public_api_client"
        )

    def test_plaidml(self):
        url = get_repo("plaidml")
        self.assertInsensitiveEqual(url, "https://github.com/plaidml/plaidml")

    def test_plaidml_vertexai(self):
        url = get_repo("https://vertexai-plaidml.readthedocs-hosted.com/")
        self.assertInsensitiveEqual(url, "https://github.com/plaidml/plaidml")

    def test_mapbox(self):
        url = get_repo("https://mapbox-mapbox.readthedocs-hosted.com/")
        self.assertInsensitiveEqual(url, "https://github.com/mapbox/mapbox-sdk-py")

        url = self.converter.get_vcs("mapbox")
        self.assertInsensitiveEqual(url, "https://github.com/mapbox/mapbox-sdk-py")

    def test_mapboxgl(self):
        url = get_repo("https://mapbox-mapboxgl-jupyter.readthedocs-hosted.com/")
        self.assertInsensitiveEqual(url, "https://github.com/mapbox/mapboxgl-jupyter")

        url = self.converter.get_vcs("mapboxgl")
        self.assertInsensitiveEqual(url, "https://github.com/mapbox/mapboxgl-jupyter")

    def test_scanpy(self):
        url = get_repo("https://icb-scanpy.readthedocs-hosted.com/")
        self.assertEqual(url, "https://github.com/theislab/scanpy")

        url = self.converter.get_vcs("scanpy")
        self.assertEqual(url, "https://github.com/theislab/scanpy")

    def test_message_ix(self):
        url = get_repo(
            "https://iiasa-energy-program-message-ix.readthedocs-hosted.com/"
        )
        self.assertEqual(url, "https://github.com/iiasa/message_ix")

        url = self.converter.get_vcs("message-ix")
        self.assertEqual(url, "https://github.com/iiasa/message_ix")

    def test_cognite_docs(self):
        url = get_repo(
            "https://cognite-docs.readthedocs-hosted.com/", strip_docs_suffix=False
        )
        self.assertEqual(url, "https://github.com/cognitedata/cognite-python-docs")

        url = self.converter.get_vcs("cognite-sdk")
        self.assertEqual(url, "https://github.com/cognitedata/cognite-sdk-python")

    def test_methylcheck(self):
        url = get_repo("https://life-epigenetics-methylcheck.readthedocs-hosted.com/")
        self.assertEqual(url, "https://github.com/LifeEGX/methylcheck")

        url = self.converter.get_vcs("methylcheck")
        self.assertInsensitiveEqual(url, "https://github.com/LifeEGX/methylcheck")

    def test_arundo_tsaug(self):
        url = get_repo("https://arundo-tsaug.readthedocs-hosted.com")
        self.assertEqual(url, "https://github.com/arundo/tsaug")

        url = self.converter.get_vcs("tsaug")
        self.assertEqual(url, "https://github.com/arundo/tsaug")

    def test_arundo_adtk(self):
        url = get_repo("https://arundo-adtk.readthedocs-hosted.com/")
        self.assertEqual(url, "https://github.com/arundo/adtk")

        url = self.converter.get_vcs("adtk")
        self.assertEqual(url, "https://github.com/arundo/adtk")

    def test_pytext(self):
        url = get_repo("https://pytext-pytext.readthedocs-hosted.com/")
        self.assertEqual(url, "https://github.com/facebookresearch/pytext")

    def test_lime_newsletter(self):
        url = get_repo("https://lime-lime-newsletter.readthedocs-hosted.com/")
        self.assertEqual(url, "https://github.com/Lundalogik/lime-newsletter")

    def test_leapyear_python(self):
        url = get_repo(
            "https://leapyear-python-docs.readthedocs-hosted.com/", version="2.9.1"
        )
        self.assertIsNone(url)  # Auth needed

    def _test_other(self):
        url = get_repo("https://totvslabs-pycarol.readthedocs-hosted.com/")
        self.assertIsNone(url)
        url = get_repo("https://scalr-athena.readthedocs-hosted.com")  # github
        self.assertIsNotNone(url)


class TestBitBucketRepo(_TestBase):
    def test_feedcache(self):
        url = get_repo("feedcache")
        self.assertEqual(url, "https://bitbucket.org/dhellmann/feedcache")

    def test_hudya_docs(self):
        url = get_repo(
            "https://hudya-docs.readthedocs-hosted.com/", strip_docs_suffix=False
        )
        self.assertEqual(url, "https://bitbucket.org/hudya/docs")

    def test_django_portlets(self):
        url = get_repo("django-portlets")
        self.assertEqual(url, "https://bitbucket.org/diefenbach/django-portlets")

    def test_django_portlets_redirect(self):
        url = self.converter.get_vcs("django-portlets")
        self.assertEqual(url, "https://github.com/diefenbach/django-portlets")
