from tests.utils import _TestBase


class TestGitHubRepo(_TestBase):
    def test_sphinxcontrib_infrae(self):
        rv = self._check_github_repo("sphinx-doc/sphinxcontrib-infrae")
        self.assertFalse(rv)

    def test_sphinxcontrib_napoleon(self):
        rv = self._check_github_repo("sphinx-contrib/napoleon")
        self.assertTrue(rv)

    def test_sphinxcontrib_websupport(self):
        rv = self._check_github_repo("sphinx-doc/sphinxcontrib-websupport")
        self.assertTrue(rv)

    def test_dedupe_variable_datetime(self):
        url = self._get_scm("dedupe-variable-datetime")
        self.assertInsensitiveEqual(
            url, "https://github.com/datamade/dedupe-variable-datetime"
        )
        rv = self._check_github_repo(url)
        self.assertFalse(rv)

    def test_nosegae(self):
        url = self._get_scm("nosegae")
        self.assertInsensitiveEqual(url, "https://github.com/Trii/NoseGAE")

    def test_fpdf(self):
        url = self._get_scm("fpdf")
        self.assertInsensitiveEqual(url, "https://github.com/reingart/pyfpdf")

    def test_flask_compress(self):
        url = self._get_scm("Flask-Compress")
        self.assertInsensitiveEqual(
            url, "https://github.com/colour-science/flask-compress"
        )
        rv = self._check_github_repo(url)
        self.assertTrue(rv)

    def test_temporary_fork_repo_metafone(self):
        url = self._get_scm("metafone")
        self.assertInsensitiveEqual(url, "https://github.com/al45tair/metaphone")
        rv = self._check_github_repo(url)
        self.assertFalse(rv)

    def test_pycountry_convert(self):
        url = self._get_scm("pycountry-convert")
        self.assertInsensitiveEqual(
            url, "https://github.com/jefftune/pycountry-convert"
        )
        rv = self._check_github_repo(url)
        self.assertTrue(rv)

    def test_bb_Adamanteus(self):
        url = self._get_scm("Adamanteus")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/Josh/adamanteus")
        rv = self._check_github_repo(url)
        self.assertFalse(rv)

    def test_bb_anyvc(self):
        url = self._get_scm("anyvc")
        self.assertInsensitiveEqual(
            url, "https://github.com/ronnypfannschmidt-attic/anyvc"
        )
        rv = self._check_github_repo(url)
        self.assertTrue(rv)

    def test_sshmount_netrc(self):
        url = self._get_scm("sshmount-netrc")
        self.assertInsensitiveEqual(
            url, "https://github.com/tjaartvdwalt/sshmount-netrc"
        )
        rv = self._check_github_repo(url)
        self.assertTrue(rv)

    def test_coveralls_check(self):
        rv = self._check_github_repo("https://github.com/cjw296/coverage-check")
        self.assertFalse(rv)

    def test_hypothesis_pytest(self):
        url = self._get_scm("hypothesis-pytest")
        self.assertInsensitiveEqual(url, "https://github.com/DRMacIver/hypothesis")
        repo = self._check_github_repo(url)
        self.assertTrue(repo)
        # TODO: resolve redirect to https://github.com/HypothesisWorks/hypothesis

    def test_vcs_mirrors(self):
        url = self._get_scm("vcs-mirrors")
        self.assertInsensitiveEqual(url, "https://github.com/pcdummy/vcs-mirrors")
        rv = self._check_github_repo(url)
        self.assertTrue(rv)

    def test_flake8_todo(self):
        url = self._get_scm("flake8-todo")
        self.assertInsensitiveEqual(url, "https://github.com/schlamar/flake8-todo")
        rv = self._check_github_repo(url)
        self.assertTrue(rv)

    def test_flake8_immediate(self):
        url = self._get_scm("flake8-immediate")
        self.assertInsensitiveEqual(url, "https://github.com/schlamar/flake8-immediate")
        rv = self._check_github_repo(url)
        self.assertTrue(rv)

        url = self._get_scm("flake8_immediate")
        self.assertInsensitiveEqual(url, "https://github.com/schlamar/flake8-immediate")
        rv = self._check_github_repo(url)
        self.assertTrue(rv)


class TestGitHubMissingRepo(_TestBase):
    def test_debian(self):
        url = self._get_scm("debian")
        self.assertInsensitiveEqual(url, "https://github.com/ourway/iran")
        rv = self._check_github_repo(url)
        self.assertFalse(rv)

    def test_nonexistant_repo_azureml(self):
        url = self._get_scm("azureml-model-management-sdk")
        self.assertInsensitiveEqual(
            url, "https://github.com/Azure/azure-ml-api-sdk-python"
        )
        rv = self._check_github_repo(url)
        self.assertFalse(rv)

    def test_nonexistant_repo_octohot(self):
        url = self._get_scm("octohot")
        self.assertInsensitiveEqual(url, "https://github.com/hotmart-org/octohot")
        rv = self._check_github_repo(url)
        self.assertFalse(rv)

    def test_nonexistant_repo_spotinst_agent(self):
        url = self._get_scm("spotinst-agent")
        self.assertInsensitiveEqual(
            url, "https://github.com/spotinst/spotinst-spectrum-agent"
        )
        rv = self._check_github_repo(url)
        self.assertFalse(rv)


class TestGitHubSetupPy(_TestBase):
    def test_putty(self):
        rv = self._check_github_setuppy("jayvdb/flake8-putty", "flake8-putty")
        self.assertTrue(rv)
        self.assertIn("putty", rv)
