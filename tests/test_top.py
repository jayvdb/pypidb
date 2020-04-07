import unittest

from unittest_expander import expand, foreach

from tests.data import bad_metadata, expected
from tests.utils import _stdlib, _TestBase, normalise_list

try:
    from tests.datasets import _intersect_stdlib, get_top_packages
except (SyntaxError, ImportError):
    raise unittest.SkipTest("Disabled on Python 2")


expected = normalise_list(expected)
bad_metadata = normalise_list(bad_metadata)

failures = []

repeat_expected = False


def _fetch_names(kind="top4kyear", xstatic=False, ignore_failures=True):
    for name in get_top_packages(kind):
        if name in _stdlib:
            continue

        if xstatic:
            if not name.startswith("xstatic-"):
                continue
        else:
            if name.startswith("xstatic-"):
                continue

        if not repeat_expected and name.lower() in expected:
            continue

        if name.lower() in [i.lower() for i in bad_metadata]:
            continue

        if ignore_failures and name in [i.lower() for i in failures]:
            continue

        yield name


_all = list(_fetch_names())
_month = list(name for name in _fetch_names("top4kmonth") if name not in _all)


@expand
class TestTopStdlib(_TestBase):

    names = list(_intersect_stdlib())
    # TestStdlibNames allows missing metadata;
    # this top class does not, as any highly used
    # bit of software should be in a VCS somewhere
    # and be findable, otherwise many eyes doesnt work.
    expected_failures = [
        "ast",
        "email",
        "enum",
        "faulthandler",
        "functools",
        "html",
        "pprint",
        "resource",
        "typing",
        "uuid",
    ]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestTop360(_TestBase):
    # 360 to match https://github.com/hugovk/drop-python/

    names = _all[:360]
    expected_failures = _TestBase.expected_failures + [
        "newrelic",
        "nvidia-ml-py3",  # new, no urls, todo?
        "ordereddict",  # old, no urls
        "termcolor",  # no vcs
        "widgetsnbextension",  # subproject of ipywidgets
    ]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestTopXStatic(_TestBase):

    names = set(_fetch_names(xstatic=True, kind="top4kyear")) | set(
        _fetch_names(xstatic=True, kind="top4kmonth")
    )

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestTopFirstThousandTail(_TestBase):

    names = _all[360:1000]
    expected_failures = _TestBase.expected_failures + [
        "google-cloud-dataflow",  # no urls
        "intel-openmp",
        "marshmallow-enum",  # no urls
        "mysql-connector-python-rf",
        "mysql-connector",
        "mysql-connector-python",
        "nvidia-ml-py",
        "requestsexceptions",  # c.f. test_openstack.py
        "newrelic",  # no urls
        "spotinst-agent",  # https://github.com/spotinst/spotinst-sdk-python/issues/65
    ]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestTopSecondThousand(_TestBase):

    names = _all[1000:2000]
    expected_failures = _TestBase.expected_failures + ["oset"]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestTopTail(_TestBase):

    names = _all[2000:]
    expected_failures = [
        "bindep",
        "clearbit",
        "comet-ml",
        "dbus-python",
        "dm.xmlsec-binding",
        "pycuda",  # repo is auth protected
        "robinhood-aiokafka",
        "scons",
        "tableauhyperapi",
        "tensorboard-plugin-wit",
    ]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])


@expand
class TestTop30Days(_TestBase):

    names = _month
    expected_failures = _TestBase.expected_failures + [
        "awshelpers",
        "azureml-mlflow",  # no urls found
        "comet-ml",
        "edx-tincan-py35",
        "clearbit",
        "kivy-deps-sdl2",  # no suitable metadata
        "mandrill-37",
        "mxnet-cu90mkl",
        "netapp-lib",
        "pretty-bad-protocol",  # todo
        "replit",
        "strsim",  # old version of strsimpy
        "testinfiniteloop",
        "tensorflow-addons",
        "watson-machine-learning-client-v4",
    ]

    @foreach(names)
    def test_package(self, name):
        self._test_names([name])
