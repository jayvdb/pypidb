from unittest_expander import expand, foreach

from tests.utils import _TestBase

# TODO: Use gitlab find https://opendev.org/explore/repos?q=requestsexceptions
openstack_none = ["microversion-parse", "requestsexceptions"]

openstack_opendev = [
    "jenkins-job-builder",
    "gear",
    "hacking",
    "mox3",
    "neutron-lib",
    "openstacksdk",
    "os-ken",
    "osc-lib",
    "pyeclib",
    "python-zaqarclient",
    "sphinx-feature-classification",
]

openstack_lp = ["lockfile"]

openstack_cgit = [
    "pbr",
    "bindep",
    "reno",
    "ldappool",
    "python-jenkins",
    "wsme",
    "glean",
    "bashate",
    "git-review",
    "python-rsdclient",
]

openstack_github = ["cliff"]


@expand
class TestOpenDev(_TestBase):

    expected_failures = ["bindep"]  # no license

    @foreach(openstack_opendev + openstack_cgit + openstack_github)
    def test_package(self, name):
        if name in self.expected_failures:
            return

        url = self.converter.get_vcs(name)
        self.assertIsNotNone(url)
        self.assertIn("//opendev.", url)
        self.assertIn("/" + name, url)


@expand
class TestOpenStackLaunchpad(_TestBase):
    @foreach(openstack_lp)
    def test_package(self, name):
        url = self.converter.get_vcs(name)
        self.assertIsNotNone(url)
        self.assertIn("//launchpad.", url)
