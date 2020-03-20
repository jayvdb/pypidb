from tests.utils import _TestBase


class TestShields(_TestBase):
    def test_invoke(self):
        url = self.converter.get_vcs("invoke")
        self.assertInsensitiveEqual(url, "https://github.com/pyinvoke/invoke")

    def test_pytest_testmon(self):
        url = self.converter.get_vcs("pytest_testmon")
        self.assertInsensitiveEqual(url, "https://github.com/tarpas/pytest-testmon")
