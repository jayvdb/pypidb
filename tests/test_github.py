from pypidb._github import check_repo, get_repo_setuppy
from tests.utils import _TestBase


class TestGitHubRepo(_TestBase):
    def test_sphinxcontrib_infrae(self):
        rv = check_repo("sphinx-doc/sphinxcontrib-infrae")
        self.assertFalse(rv)

    def test_sphinxcontrib_napoleon(self):
        rv = check_repo("sphinx-contrib/napoleon")
        self.assertTrue(rv)

    def test_sphinxcontrib_websupport(self):
        rv = check_repo("sphinx-doc/sphinxcontrib-websupport")
        self.assertTrue(rv)

    def test_dedupe_variable_datetime(self):
        url = self.converter.get_vcs("dedupe-variable-datetime")
        self.assertInsensitiveEqual(
            url, "https://github.com/datamade/dedupe-variable-datetime"
        )
        rv = check_repo(url)
        self.assertFalse(rv)

    def test_nosegae(self):
        url = self.converter.get_vcs("nosegae")
        self.assertInsensitiveEqual(url, "https://github.com/Trii/NoseGAE")

    def test_fpdf(self):
        url = self.converter.get_vcs("fpdf")
        self.assertInsensitiveEqual(url, "https://github.com/reingart/pyfpdf")

    def test_flask_compress(self):
        url = self.converter.get_vcs("Flask-Compress")
        self.assertInsensitiveEqual(
            url, "https://github.com/colour-science/flask-compress"
        )
        rv = check_repo(url)
        self.assertTrue(rv)

    def test_temporary_fork_repo_metafone(self):
        url = self.converter.get_vcs("metafone")
        self.assertInsensitiveEqual(url, "https://github.com/al45tair/metaphone")
        rv = check_repo(url)
        self.assertFalse(rv)

    def test_pycountry_convert(self):
        url = self.converter.get_vcs("pycountry-convert")
        self.assertInsensitiveEqual(
            url, "https://github.com/jefftune/pycountry-convert"
        )
        rv = check_repo(url)
        self.assertTrue(rv)

    def test_bb_Adamanteus(self):
        url = self.converter.get_vcs("Adamanteus")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/Josh/adamanteus")
        rv = check_repo(url)
        self.assertFalse(rv)

    def test_bb_anyvc(self):
        url = self.converter.get_vcs("anyvc")
        self.assertInsensitiveEqual(
            url, "https://github.com/ronnypfannschmidt-attic/anyvc"
        )
        rv = check_repo(url)
        self.assertTrue(rv)

    def test_sshmount_netrc(self):
        url = self.converter.get_vcs("sshmount-netrc")
        self.assertInsensitiveEqual(
            url, "https://github.com/tjaartvdwalt/sshmount-netrc"
        )
        rv = check_repo(url)
        self.assertTrue(rv)

    def test_coveralls_check(self):
        rv = check_repo("https://github.com/cjw296/coverage-check")
        self.assertFalse(rv)

    def test_hypothesis_pytest(self):
        url = self.converter.get_vcs("hypothesis-pytest")
        self.assertInsensitiveEqual(url, "https://github.com/DRMacIver/hypothesis")
        repo = check_repo(url)
        self.assertTrue(repo)
        # TODO: resolve redirect to https://github.com/HypothesisWorks/hypothesis

    def test_vcs_mirrors(self):
        url = self.converter.get_vcs("vcs-mirrors")
        self.assertInsensitiveEqual(url, "https://github.com/pcdummy/vcs-mirrors")
        rv = check_repo(url)
        self.assertTrue(rv)

    def test_flake8_todo(self):
        url = self.converter.get_vcs("flake8-todo")
        self.assertInsensitiveEqual(url, "https://github.com/schlamar/flake8-todo")
        rv = check_repo(url)
        self.assertTrue(rv)

    def test_flake8_immediate(self):
        url = self.converter.get_vcs("flake8-immediate")
        self.assertInsensitiveEqual(url, "https://github.com/schlamar/flake8-immediate")
        rv = check_repo(url)
        self.assertTrue(rv)

        url = self.converter.get_vcs("flake8_immediate")
        self.assertInsensitiveEqual(url, "https://github.com/schlamar/flake8-immediate")
        rv = check_repo(url)
        self.assertTrue(rv)


class TestGitHubMissingRepo(_TestBase):
    def test_debian(self):
        url = self.converter.get_vcs("debian")
        self.assertInsensitiveEqual(url, "https://github.com/ourway/iran")
        rv = check_repo(url)
        self.assertFalse(rv)

    def test_nonexistant_repo_azureml(self):
        url = self.converter.get_vcs("azureml-model-management-sdk")
        self.assertInsensitiveEqual(
            url, "https://github.com/Azure/azure-ml-api-sdk-python"
        )
        rv = check_repo(url)
        self.assertFalse(rv)

    def test_nonexistant_repo_octohot(self):
        url = self.converter.get_vcs("octohot")
        self.assertInsensitiveEqual(url, "https://github.com/hotmart-org/octohot")
        rv = check_repo(url)
        self.assertFalse(rv)

    def test_nonexistant_repo_spotinst_agent(self):
        url = self.converter.get_vcs("spotinst-agent")
        self.assertInsensitiveEqual(
            url, "https://github.com/spotinst/spotinst-spectrum-agent"
        )
        rv = check_repo(url)
        self.assertFalse(rv)


class TestGitHubSetupPy(_TestBase):
    def test_putty(self):
        rv = get_repo_setuppy("jayvdb/flake8-putty", "flake8-putty")
        self.assertTrue(rv)
        self.assertIn("putty", rv)
