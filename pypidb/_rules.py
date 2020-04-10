from functools import partial
import os.path

from appdirs import user_cache_dir
from logging_helper import setup_logging

import dns_cache.expiration
from dns_cache import NO_EXPIRY, override_system_resolver
from dns_cache.diskcache import DiskCache
from pypidb import __name__ as app_name

from ._cache import cache_subdir
from ._db import multipackage_repos, reverse_mappings
from ._patch import (
    _get_patch_redirects,
    _get_raw_patch_url,
)
from ._url_extract import (
    get_html_hrefs,
    _url_extract_both,
    _url_extractor_wrapper,
    _url_extractor_wrapper_no_dns,
    _url_no_extract,
)
from ._scm_url_cleaner import _match_hostname
from ._similarity import normalize

logger = setup_logging()

dns_cache.expiration.MIN_TTL = NO_EXPIRY

_azure_exclude = [
    "azure-batch-samples",
    "azure-samples",
    "azureml-containers",
    "azureml-sdk-for-r",
    "azuresearch_jfk_files",
    "botframework-solutions",
    "cla-assistant",
    "machinelearningnotebooks",
    "microsoft/ai",
    "mlops",
    "open-telemetry/opencensus-website",  # azure-core-tracing-opencensus
    "open-telemetry/opentelemetry-python",  # "
]


class NoExpirationDiskCache(DiskCache, dns_cache.expiration.NoExpirationCache):
    pass


dns_cache_dirpath = cache_subdir("dns")
dns_cache = NoExpirationDiskCache(directory=dns_cache_dirpath, min_ttl=NO_EXPIRY)
resolver = override_system_resolver(cache=dns_cache)


def preload_reject_match(name, url):
    name = normalize(name)
    existing_result = reverse_mappings.get(url.lower())
    if existing_result and existing_result != name:
        for base in multipackage_repos:
            if url.startswith(base):
                break
        else:
            logger.debug(
                "url {} rejected as it belongs to {}".format(url, existing_result)
            )
            return True
    return False


class Rule(object):
    def __init__(self, name, preload=None, **kwargs):
        self.name = name
        self.key = normalize(name)
        self.match = self.key
        self.preload = preload
        self.fetch_count = 5
        assert preload is None or isinstance(preload, list)
        self.reject_match_func = None
        self.expect_none = False
        self.ignore_bad_metadata = False
        self.patch = False
        self.ignore_urls = []  # FIXME: does not ignore if url has a path
        self.link_extract = _url_extractor_wrapper
        self._data = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return "{}/{} = {} {!r} {!r}".format(
            self.key, self.match, self.name, self.preload, self._data
        )

    def url_redirects(self):
        if not self.patch:
            return

        url = _get_raw_patch_url(self.patch)

        import requests

        response = requests.get(url)

        assert response.headers["content-type"].startswith(
            "text/plain"
        ), response.headers["content-type"]
        redirects = _get_patch_redirects(response.content, allow_add_only=True)
        assert redirects
        return redirects

    def reject_match(self, name, url):
        name = self.match
        if self.preload:
            if preload_reject_match(name, url):
                return True
        if self.reject_match_func:
            rv = self.reject_match_func(name, url)
            logger.info(
                "{} rejecting match {} {}".format(self.reject_match_func, name, url)
            )
            return rv

    def reject_url(self, name, url):
        if self.ignore_urls:
            for rule in self.ignore_urls:
                require_no_path = "/" not in rule
                if _match_hostname(url, rule, require_no_path=require_no_path):
                    return True

            if url in self.ignore_urls:
                return True
        return False

    def hash(self):
        return self.key


def xstatic_reject_match(name, url):
    if name.lower().startswith("xstatic") and "xstatic" not in url.lower():
        return True


def reject_docs_match(name, url):
    if not name.lower().startswith("docs") and "docs" in url.lower():
        return True


def reject_names(name, url, names):
    for name in names:
        if name in url.lower():
            return True


def ms_azure_reject_match(name, url):
    if url.endswith("azure/azure-sdk"):
        return True
    return reject_names(name, url, _azure_exclude)


def libvirt_hack(name, url):
    if url.startswith("https://gitlab.com/libvirt/libvirt"):
        return url.replace("/-/blob/master/docs/index.html.in", "-python")


def combine(name, url, funcs):
    for func in funcs:
        if func(name, url):
            return True


class DefaultRule(Rule):
    def __init__(self, name, preload=None, **kwargs):
        key = normalize(name)
        if key.startswith("xstatic-"):
            kwargs["reject_match_func"] = xstatic_reject_match
        elif key.startswith("azure") or key == "onedrivesdk":
            if key != "azure":
                preload = ["azure"]
            if key == "azure-kusto-ingest":
                preload = ["azure", "jupyterhub"]
            if key == "azureml-mlflow":
                preload = ["azure", "mlflow"]
            kwargs["reject_match_func"] = partial(
                combine, funcs=[reject_docs_match, ms_azure_reject_match]
            )
            if key == "azure-cosmosdb-table":
                kwargs["repo_filename"] = "build_packages.py"
            elif key.startswith("azure-storage-"):
                kwargs["repo_filename"] = "tool_build_packages.py"
            else:
                kwargs["repo_filename"] = "README.md"
            kwargs["ignore_urls"] = [
                "readthedocs.org",  # azure-monitor
                "dev.azure.com",
            ]
        elif key.startswith("sphinxcontrib-"):
            kwargs["ignore_urls"] = ["sphinx-doc.org", "sphinx.pocoo.org"]
        elif key == "jupyter-js-widgets-nbextension":
            preload = ["jupyter", "jupyterhub", "ipython"]
            kwargs["ignore_urls"] = ["jupyter.org/about", "ipython.org"]
        elif (
            key.startswith("jupyter-")
            or key.startswith("jupyterlab-")
            or key.startswith("nb")
            or key in ["jupyter", "ipysheet"]
        ):
            preload = ["jupyterhub"]
            kwargs["ignore_urls"] = ["jupyter.org"]
        elif (key.startswith("ipy") and key != "ipython") or key in [
            "widgetsnbextension",
            "traittypes",
            "traitlets",
        ]:
            preload = ["ipython"]
            kwargs["ignore_urls"] = ["ipython.org"]
        elif key.startswith("orange-") or key.startswith("orange3-"):
            preload = ["orange3"]
        elif key.startswith("moz"):
            preload = ["sphinx", "sphinx-rtd-theme", "requests"]
        elif key.startswith("kivy-deps-"):
            kwargs["ignore_urls"] = ["kivy.org"]
        elif key in ("turbogears2",):
            preload = ["bzr"]
        elif key in ("turbogears", "turbomail"):
            pass
        elif key.startswith("tg") or key.startswith("turbo"):
            preload = [
                "turbogears2",
                "turbogears",
                "readthedocs-org",
                "fabric",
                "sphinx-rtd-theme",
            ]
        elif key.startswith("gax-google-") or key.startswith("gapic-"):
            preload = ["google-gax", "virtualenv"]
        elif key.startswith("h2o-pysparkling"):
            # https://github.com/h2oai/sparkling-water/issues/1953
            kwargs["ignore_urls"] = ["docs.h2o.ai"]
            preload = ["sphinx-rtd-theme"]
        elif key.startswith("ujson-"):
            kwargs["match"] = key.replace("ujson", "ultrajson")

        super(DefaultRule, self).__init__(name, preload, **kwargs)


class Rules(dict):
    def from_set(self, other):
        for item in other:
            self[item.key] = item


rules = Rules()
rules.from_set(
    {
        Rule("aexpect", ["avocado-framework"]),
        Rule(
            "amazon-dax-client",
            ["boto3", "botocore"],
            ignore_urls=["docs.aws.amazon.com"],
            expect_none=True,
        ),
        Rule("antlr-python-runtime", ignore_bad_metadata=True),
        Rule("antlr3-python-runtime", ["antlr4-python3-runtime"]),
        Rule("anyvc", patch="https://github.com/RonnyPfannschmidt-Attic/anyvc/pull/1"),
        Rule("archinfo", patch="https://github.com/angr/archinfo/pull/83"),
        Rule("aspects", ignore_urls=["www.logilab.org"], expect_none=True),
        Rule(
            "awsebcli",
            ["pip"],
            ignore_urls=["docs.aws.amazon.com", "aws.amazon.com"],
            link_extract=_url_no_extract,
            expect_none=True,
        ),
        Rule("awshelpers", link_extract=_url_no_extract, expect_none=True),
        Rule("aws-sam-translator", ["aws-sam-cli"]),
        Rule("awsretry", ignore_bad_metadata=True),
        Rule("backports", ignore_bad_metadata=True),
        Rule("barnum", ignore_urls=["wordpress.org"]),
        Rule("basemap", ignore_bad_metadata=True),
        Rule("bindep", ["project-config"], expect_none=True),
        Rule("bitvector", ignore_urls=["sun.com"], expect_none=True),
        Rule("bobo", repo_filename="buildout.cfg"),
        Rule(
            "bugsnag", ignore_urls=["www.bugsnag.com", "bugsnag.com"], expect_none=True
        ),
        Rule("bugzilla", link_extract=get_html_hrefs),
        Rule("camelot", ignore_urls=["www.python-camelot.com"], expect_none=True),
        Rule("cassandra-driver", match="datastax-python-driver"),
        Rule("catkin", ignore_bad_metadata=True),
        Rule("ccxt", ignore_urls=["ccxt.trade"]),
        Rule("cdecimal", ignore_bad_metadata=True),
        Rule("celery-redbeat", ["celery"]),
        Rule("cffi", patch="https://foss.heptapod.net/pypy/cffi/commit/9b98da72.patch"),
        Rule("cfscrape", ignore_urls=["nodejs.org"]),
        Rule("cheesecake", link_extract=_url_no_extract, expect_none=True),
        Rule("cheetah", ignore_urls=["pythonhosted.org"]),
        Rule("clickhouse-cityhash", ["cityhash", "xxh", "metrohash"]),
        Rule(
            "cloudshell-automation-api",
            ignore_urls=["www.qualisystems.com"],
            expect_none=True,
        ),
        Rule("coards", ["sphinx-rtd-theme", "zc-buildout"]),
        Rule("cogapp", ignore_urls=["rubyforge.org"]),
        Rule("collectd", ignore_bad_metadata=True),
        Rule("comet-ml", ignore_urls=["comet.ml", "www.comet.ml"], expect_none=True),
        Rule("compatibility-lib", ignore_urls=["www.docker.com"], expect_none=True),
        Rule("compressed-segmentation", ignore_urls=["www.janelia.org"]),
        Rule("config", ignore_urls=["docs.red-dove.com"]),
        Rule("contextual", ignore_bad_metadata=True),
        Rule("cronwatch", ignore_bad_metadata=True),
        Rule(
            "coveralls-check", patch="https://github.com/cjw296/coveralls-check/pull/2"
        ),
        Rule("ctypeslib", ignore_bad_metadata=True),
        Rule("cvxopt", ["sphinx-rtd-theme"], expect_none=True),
        Rule(
            "darcsver",
            ["babel", "tahoe-lafs"],
            ignore_urls=["peak.telecommunity.com", "trac.edgewall.org"],
            expect_none=True,
        ),
        Rule("dash-table", repo_filename="package.json"),
        Rule("databricks-connect", link_extract=_url_no_extract, expect_none=True),
        Rule("datadog-checks-base", match="integrations-core"),
        Rule("dbf", ["epydoc"], expect_none=True),
        Rule(
            "dbus-python",
            ["pyqt5", "pygobject"],
            ignore_urls=["www.riverbankcomputing.co.uk/software/pyqt/intro"],
            expect_none=True,
        ),
        Rule(
            "dbus-signature-pyparsing",
            patch="https://github.com/stratis-storage/dbus-signature-pyparsing/pull/13",
        ),
        Rule("debian", ignore_bad_metadata=True),
        Rule(
            "dephell-pythons", patch="https://github.com/dephell/dephell_pythons/pull/8"
        ),
        Rule(
            "dephell-shells", patch="https://github.com/dephell/dephell_shells/pull/3"
        ),
        Rule("dai-sgqlc-3-5", ["sgqlc"], link_extract=_url_no_extract, expect_none=True),
        Rule("dateutils", patch="https://github.com/jmcantrell/python-dateutils/pull/8"),
        Rule("divide-and-cover", ignore_urls=["unmaintained.tech"], expect_none=True),
        Rule(
            "django-articles",
            patch="https://github.com/codekoala/django-articles/pull/12",
        ),
        Rule("django-common-helpers", ignore_urls=["tivix.com"]),
        Rule("django-datagrid", ignore_urls=["www.agiliq.com"], expect_none=True),
        Rule(
            "django-events", patch="https://github.com/skyl/django-eventpickrs/pull/1"
        ),
        Rule(
            "django-hijack-admin",
            patch="https://github.com/arteria/django-hijack-admin/commit/e0773ff37.patch",
        ),
        Rule("django-inline-ordering", link_extract=_url_no_extract, expect_none=True),
        Rule("django-lfs"),
        Rule("django-lfstheme", ["django-lfs"], expect_none=True),
        Rule(
            "django-portlets",
            patch="https://github.com/diefenbach/django-portlets/pull/2",
        ),
        Rule(
            "django-settings-toml",
            ["django"],
            link_extract=_url_no_extract,
            expect_none=True,
        ),
        Rule(
            "django-staticmediamgr", ignore_urls=["www.crockford.com"], expect_none=True
        ),
        Rule(
            "django-settings-toml",
            patch="https://github.com/maxking/django-settings-toml/pull/5",
        ),
        Rule("django-toolbelt", ignore_urls=["devcenter.heroku.com"], expect_none=True),
        Rule("djtracker", ignore_urls=["www.f4ntasmic.com", "mark-rogers.net"]),
        Rule("dm-xmlsec-binding", ["lxml"], expect_none=True),
        Rule("dox", ["boot2docker"], expect_none=True),
        Rule(
            "drfdocs",
            patch="https://github.com/manosim/django-rest-framework-docs/pull/186",
        ),
        Rule("elementtidy", ignore_bad_metadata=True),
        Rule(
            "encutils",
            ["cssutils"],
            link_extract=get_html_hrefs,
            match="cssutils",
            expect_none=True,
        ),
        Rule("enum", ["enum34", "roundup"], expect_none=True),
        Rule(
            "epl",
            [
                "pip",
                "pipenv",
                "virtualenv",
                "virtualenvwrapper",
                "pipfile",
                "sphinx-rtd-theme",
            ],
            ignore_urls=["virtualenv.pypa.io"],
            expect_none=True,
        ),
        Rule("etsdevtools", ignore_bad_metadata=True),
        Rule("exifread", ["pip", "setuptools"]),
        Rule("fabric", ignore_urls=["fabfile.org", "paramiko.org", "pyinvoke.org"]),
        Rule("fabric2", ignore_urls=["fabfile.org", "paramiko.org", "pyinvoke.org"]),
        Rule("featureflow", patch="https://github.com/JohnVinyard/featureflow/pull/10"),
        Rule("firkin", ["epydoc"], expect_none=True),
        Rule(
            "flake8-immediate",
            patch="https://github.com/schlamar/flake8-immediate/commit/8121d2eb.patch",
        ),
        Rule(
            "flask-compress",
            patch="https://github.com/colour-science/flask-compress/pull/2",
        ),
        Rule("fluidity-sm", ignore_bad_metadata=True),
        Rule("fs", match="pyfilesystem2"),
        Rule(
            "fsspec",
            ["black", "tox", "pre-commit", "tox-conda"],
            link_extract=_url_no_extract,
        ),
        Rule("galaxy", ignore_urls="galaxyproject.org", ignore_bad_metadata=True),
        Rule("galaxy-lib", ["galaxy"]),
        Rule("geopandas", ["shapely"]),
        Rule("getchanges", patch="https://github.com/TheKevJames/getchanges/pull/43"),
        Rule(
            "git-pylint-commit-hook",
            patch="https://github.com/sebdah/git-pylint-commit-hook/pull/74",
        ),
        Rule("github-release", ignore_urls=["dev.hubspot.com"], expect_none=True),
        Rule("gloo", link_extract=_url_no_extract, expect_none=True),
        Rule("gnupginterface", match="py-gnupg", ignore_bad_metadata=True),
        Rule("google-api-core", ["alabaster"]),
        Rule("google-auth", ignore_bad_metadata=True),
        Rule("google-gax", match="gax-python"),
        Rule("google-oauth", ignore_bad_metadata=True),
        Rule("google", ignore_urls=["breakingcode.wordpress.com"], expect_none=True),
        Rule(
            "googleapis-common-protos",
            patch="https://github.com/googleapis/googleapis/pull/204",
            reject_match_func=lambda name, url: "google/googleapis" in url,
        ),
        Rule("grin", patch="https://github.com/rkern/grin/commit/3cda44a6.patch"),
        Rule("gsutil", ignore_urls=["cloud.google.com/storage/docs/gsutil_install"]),
        Rule("hacking", ["pep8"]),
        Rule("haproxyctl", ignore_bad_metadata=True),
        Rule("hs-dbus-signature", patch="https://github.com/stratis-storage/hs-dbus-signature/pull/31"),
        Rule("hypothesis-pytest", ["hypothesis"], expect_none=True),
        Rule("imagecodecs", link_extract=get_html_hrefs),
        Rule("imreg", link_extract=get_html_hrefs),
        Rule("infi-clickhouse-orm", repo_filename="buildout.cfg"),
        Rule("infi-execute", repo_filename="buildout.cfg"),
        Rule(
            "intel-openmp",
            ignore_urls=["software.intel.com"],
            link_extract=_url_no_extract,
            expect_none=True,
        ),
        Rule(
            "ipympl", ["matplotlib"], ignore_urls=["matplotlib.org"], expect_none=True
        ),
        Rule("ipynb", patch="https://github.com/ipython/ipynb/pull/47"),
        Rule("juicer", repo_filename="setup.py.in"),
        Rule(
            "jupyter-c-kernel",
            patch="https://github.com/brendan-rius/jupyter-c-kernel/pull/49",
        ),
        Rule("jupyter-nbformat", ignore_bad_metadata=True),
        Rule("k5test", patch="https://github.com/pythongssapi/k5test/pull/10"),
        Rule("kaitaistruct", ["construct"]),
        Rule("keras-mxnet", ["keras"]),
        Rule("kitchen", ["hashlib"], expect_none=True),
        Rule("libarchive", match="PyEasyArchive"),  # libarchive
        Rule("librato-metrics", ignore_urls=["dev.librato.com"]),
        Rule("libvirt-python", reject_match_func=libvirt_hack),
        Rule("lightblue", ignore_bad_metadata=True),
        Rule("log4tailer", ignore_bad_metadata=True),
        Rule(
            "logentries",
            ["logentries-lecli"],
            ignore_urls=["logentries.com"],
            expect_none=True,
        ),
        Rule("logging", link_extract=_url_no_extract, expect_none=True),
        Rule("magic", ignore_bad_metadata=True),
        Rule("magma-lang", link_extract=_url_no_extract),
        Rule(
            "mailgun",
            ignore_urls=[
                "documentation.mailgun.com",
                "documentation.mailgun.net",
                "mailgun.net",
            ],
            link_extract=_url_no_extract,
            expect_none=True,
        ),
        Rule("mastodon", ignore_bad_metadata=True),
        Rule("maxminddb", match="maxmind-db-reader-python"),
        Rule(
            "membrete",
            ["django-contact-form"],
            ignore_urls=["bazaar-vcs.org"],
            expect_none=True,
        ),
        Rule("meta", ignore_urls=["semver.org"]),
        Rule("mimeparse", ignore_bad_metadata=True),
        Rule("mongoalchemy", expect_none=True),
        Rule("msgpack-python", fetch_count=1),
        Rule("myghty", ["dogpile-cache"], expect_none=True),
        Rule("neptune-client", ["neptune-contrib"], expect_none=True),
        Rule(
            "newrelic",
            ignore_urls=["newrelic.com", "docs.newrelic.com"],
            link_extract=_url_no_extract,
            expect_none=True,
        ),
        Rule(
            "newrelic-plugin-agent",
            patch="https://github.com/MeetMe/newrelic-plugin-agent/commit/e60e98d7.patch",
        ),
        Rule("nimoy-framework", match="nimoy"),  # spock
        Rule("node-semver", match="python-semver"),
        Rule("nose-fixes", ["nose", "nose2", "pytest"], expect_none=True),
        Rule("nvidia-ml-py", ["docutils"], expect_none=True),
        Rule(
            "nxapi-plumbing", patch="https://github.com/ktbyers/nxapi-plumbing/pull/10"
        ),
        Rule("numarray", ignore_bad_metadata=True),
        Rule("optcomplete", ignore_bad_metadata=True),
        Rule("overtest", link_extract=_url_no_extract, expect_none=True),
        Rule(
            "packit",
            ["setuptools", "cython", "pip", "packaging", "platter", "pbr", "wheel"],
            expect_none=True,
        ),
        Rule("pafy", patch="https://github.com/mps-youtube/pafy/pull/249"),
        Rule(
            "parse-accept-language",
            patch="https://github.com/xelven/parse-accept-language/pull/1",
        ),
        Rule("pep8", ["pycodestyle"]),
        Rule("pdfminer3k", ignore_bad_metadata=True),
        Rule("peak", ignore_bad_metadata=True),
        Rule("peak-rules", ignore_bad_metadata=True),
        Rule("pigpio", link_extract=_url_extract_both),
        Rule("pinax", ["django"], expect_none=True),
        Rule("pip-requ", ["setuptools-gitver"]),
        Rule("plaintable", patch="https://github.com/jonathaneunice/plaintable/pull/1"),
        Rule("printdebug", ["colr"], expect_none=True),
        Rule(
            "proboscis", patch="https://github.com/rackerlabs/python-proboscis/pull/28"
        ),
        Rule("py9p", repo_filename="setup.py.in"),
        Rule("pyaml", match="pretty-yaml"),
        Rule("pyastronomy", link_extract=get_html_hrefs, fetch_count=20),
        Rule("pybrain", ignore_bad_metadata=True),
        Rule("pycddb", ignore_bad_metadata=True),
        Rule("pycotap", link_extract=get_html_hrefs),
        Rule(
            "pycountry-convert",
            patch="https://github.com/jefftune/pycountry-convert/pull/1",
        ),
        Rule("pyficache", ["coverage"], repo_filename="__pkginfo__.py"),
        Rule("pyfim", ignore_urls=["www.borgelt.net"], expect_none=True),
        Rule("pygal", patch="https://github.com/Kozea/pygal/pull/494"),
        Rule("pygam", repo_filename="flit.ini"),
        Rule(
            "pygobject",
            link_extract=get_html_hrefs,
            ignore_urls=["ftp.acc.umu.se", "python-gtk-3-tutorial.readthedocs.io"],
        ),
        Rule(
            "pygtk",
            link_extract=get_html_hrefs,
            ignore_urls=["ftp.acc.umu.se", "python-gtk-3-tutorial.readthedocs.io"],
        ),
        Rule("pyke", ignore_bad_metadata=True),
        Rule("pylirc", ignore_urls=["www.lirc.org"]),
        Rule("pymetar", ["future"]),
        Rule("pymf", ignore_bad_metadata=True),
        Rule("pymilia", ignore_urls=["www.boost.org"], ignore_bad_metadata=True),
        Rule("pymilter", patch="https://github.com/sdgathman/pymilter/pull/36"),
        Rule("pymock", link_extract=get_html_hrefs, ignore_bad_metadata=True),
        Rule("pyqt4", ignore_bad_metadata=True),
        Rule("pyrex", ignore_bad_metadata=True),
        Rule(
            "pyro",
            ["pyro4"],
            ignore_urls=["java.sun.com", "www.corba.org"],
            expect_none=True,
        ),
        Rule("pyrouge", ignore_bad_metadata=True),
        Rule("pysphere", ignore_bad_metadata=True),
        Rule("pysmt", ["z3-solver"]),
        Rule("pystatgrab", ignore_bad_metadata=True),
        Rule("pytest-server-fixtures", ["python-jenkins"]),
        Rule("pytext", link_extract=_url_no_extract),
        Rule(
            "python-igraph",
            ["pycairo", "cairocffi"],
            patch="https://github.com/igraph/python-igraph/commit/9adcf87.patch",
        ),
        Rule("python-mhash", ignore_bad_metadata=True),
        Rule("python-owasp-zap-v2-4", match="zap-api-python"),
        Rule(
            "python-pseudorandom",
            patch="https://github.com/smathot/python-pseudorandom/pull/1",
        ),
        Rule("python-qt5", ignore_bad_metadata=True),
        Rule("python-registry", patch="https://github.com/williballenthin/python-registry/pull/97"),
        Rule("pytidylib", link_extract=_url_no_extract, expect_none=True),
        Rule("py-trello", ["tox"], patch="https://github.com/sarumont/py-trello/pull/309"),
        Rule("pyviz-comms", ["pyviz", "jupyterlab"]),
        Rule("pyvows", patch="https://github.com/heynemann/pyvows/pull/135"),
        Rule("pyz3950", ignore_bad_metadata=True),
        Rule("quickproxy", ["tornado-proxy"], expect_none=True),
        Rule("repoze-sphinx-autointerface", ["docutils"]),
        Rule("repoze-who-plugins-sa", match="repoze-who-sqlalchemy"),
        Rule("requests-opentracing", match="python-requests"),
        Rule(
            "requests-threads",
            patch="https://github.com/requests/requests-threads/commit/5cda6.patch",
        ),
        Rule(
            "respite",
            patch="https://github.com/jgorset/django-respite/commit/6c91a4b.patch",
        ),
        Rule("reviewboard", link_extract=_url_no_extract, expect_none=True),
        Rule("rfc6555", ignore_bad_metadata=True),
        Rule("robinhood-aiokafka", ["aiokafka"], link_extract=_url_no_extract, expect_none=True),
        Rule("rook", ignore_urls=["rookout.com"], expect_none=True),
        Rule("rpy2", patch="https://github.com/rpy2/rpy2/commit/ededbbf.patch"),
        Rule("ruffus", patch="https://github.com/cgat-developers/ruffus/pull/118"),
        Rule("s3cmd", patch="https://github.com/s3tools/s3cmd/commit/8d314b01.patch"),
        Rule("s3pip", ["django-tastypie"], ignore_urls=["jlafon.io"], expect_none=True),
        Rule("salt", ignore_urls=["saltstack.org", "repo.saltstack.com"]),
        Rule(
            "scikits-sparse",
            match="scikit-sparse",
            patch="https://github.com/scikit-sparse/scikit-sparse/commit/66b3a518.patch",
        ),
        Rule(
            "scitools",
            patch="https://github.com/hplgit/scitools/pull/45",
            ignore_bad_metadata=True,
        ),
        Rule("schevodurus", ignore_bad_metadata=True),
        Rule("scm-git", ["sampleproject"], expect_none=True),
        Rule("seqdiag", ["nwdiag"]),
        Rule("setuptools-cython", ignore_urls=["mail.python.org"], expect_none=True),
        Rule("shiboken2", ["pyside2"], expect_none=True),
        Rule("shippo", ignore_urls=["goshippo.com"], expect_none=True),
        Rule("should-dsl", patch="https://github.com/nsi-iff/should-dsl/pull/37"),
        Rule("silver-platter", ["dulwich"]),
        Rule("simplegeneric", link_extract=_url_no_extract),
        Rule("simpletal", ignore_bad_metadata=True),
        Rule(
            "singer-python",
            ignore_urls=["Singer.io/", "singer.io", "www.singer.io"],
            expect_none=True,
        ),
        Rule("skl2onnx", ["scikit-learn"]),
        Rule("spark-sklearn", repo_filename="build.sbt"),
        Rule("sphinxcontrib-napoleon", ["numpy"]),
        Rule("sphinxcontrib-youtube", ignore_bad_metadata=True),
        Rule(
            "sshmount-netrc",
            ignore_urls=["github.com"],
            ignore_bad_metadata=True,
            reject_match_func=lambda name, url: url
            == "https://github.com/tjaartvdwalt/tclt",
        ),
        Rule("sst", ["pip", "pip-tools"], match="selenium-simple-test"),
        Rule("stacks", ignore_urls=["jimmyg.org"], expect_none=True),
        Rule("strictyaml", ["pykwalify"]),
        Rule(
            "stsci-distutils", ["pyfits", "drizzlepac"], ignore_urls=["www.stsci.edu"]
        ),
        Rule(
            "stscipython",
            ["drizzlepac"],
            link_extract=_url_no_extract,
            expect_none=True,
            ignore_urls=["www.stsci.edu"],
        ),
        Rule("subgrab", patch="https://github.com/RafayGhafoor/Subscene-Subtitle-Grabber/pull/7"),
        Rule("supercaptcha", ["django"], expect_none=True),
        Rule("swapper", ["vera"]),
        Rule("sysv-ipc", ["posix-ipc"]),
        Rule("tableauhyperapi", ["tableauserverclient"], expect_none=True),
        Rule("telepathy", ["insights"]),
        Rule("tensorboard", repo_filename="package.json"),
        Rule(
            "tgfastdata",
            ["turbogears2", "toscawidgets", "virtualenv"],
            expect_none=True,
        ),
        Rule("tifffile", link_extract=get_html_hrefs),
        Rule("timer2", patch="https://github.com/ask/timer2/pull/3"),
        Rule("toastcord", ["hikari"], expect_none=True),
        Rule(
            "toscawidgets",
            ["turbogears2", "tw2-core", "pyramid", "genshi"],
            expect_none=True,
        ),
        Rule("travis", link_extract=_url_no_extract, expect_none=True),
        Rule("triforce", ["pipsi", "git-spindle"], expect_none=True),
        Rule("tlslite", patch="https://github.com/trevp/tlslite/pull/123"),
        Rule("turbocheetah", ["turbogears2", "fabric", "sphinx-rtd-theme"]),
        Rule("turbogears", ["turbogears2", "pyramid", "genshi"]),
        Rule("tw-dynforms", ["tw2-core"], expect_none=True),
        Rule(
            "tw-forms", ["tw2-core"], ignore_urls=["toscawidgets.org"], expect_none=True
        ),
        Rule("typing", expect_none=True),
        Rule("typogrify-engineer", preload=["typogrify", "engineer"], expect_none=True),
        Rule("ujson-bedframe", match="ultrajson-esnme"),
        Rule("ujson", match="ultrajson"),
        Rule("uuid", link_extract=get_html_hrefs),
        Rule("uwsgitop", patch="https://github.com/xrmx/uwsgitop/pull/60"),
        Rule("uwsgitop", patch="https://github.com/xrmx/uwsgitop/pull/60"),
        Rule("viper", ignore_urls=["fenicsproject.org"], expect_none=True),
        Rule("waiting", ["sphinx-rtd-theme", "flux"]),
        Rule("watson-machine-learning-client", ["alabaster"], expect_none=True),
        Rule("webapp", ignore_bad_metadata=True),
        Rule("webunit", ["docutils"], expect_none=True),
        Rule("wmi", ["pywin32"], expect_none=True),
        Rule("wordaxe", ignore_bad_metadata=True),
        Rule("xpyb", ignore_bad_metadata=True),
        Rule("xml2rfc", ["weasyprint"]),
        Rule("xmltramp", ignore_bad_metadata=True),
        Rule(
            "yubico",
            ["fido2", "yubihsm"],
            ignore_urls=["www.yubico.com", "api.yubico.com"],
            link_extract=_url_no_extract,
        ),
        Rule("yubihsm", ignore_urls=["developers.yubico.com"]),
        Rule("z3c-testsetup", ["zope-app-testing", "zope-testing"]),
        Rule("zabbix-api", ignore_urls=["www.zabbix.com"]),
        Rule("zendesk", patch="https://github.com/maxgutman/zendesk/pull/12"),
        Rule("zsi", ignore_bad_metadata=True),
        Rule(
            "zuul-sphinx",
            ["zuul", "alabaster"],
            ignore_urls=["zuul-ci.org"],
            expect_none=True,
        ),
        Rule("zvmcloudconnector", ["zhmcclient"]),
    }
)

_email_matches = {
    "avocado-devel@redhat.com": "avocado-framework",
    "cgohlke@uci.edu": "cgohlke",
    "colm.oconnor.github@gmail.com": ["hitchdev", "crdoconnor"],
    "developers@pyviz.org": "holoviz/{namespace}_{suffix}",
    "dthomas@osrfoundation.org": ["ros", "ros-infrastructure"],
    "darcy@PyGreSQL.org": "pygresql",
    "efried@us.ibm.com": "powervm",
    "enthought-dev@enthought.com": "srossross",
    "f4nt@f4ntasmic.com": "f4nt",
    "galaxy-dev@lists.galaxyproject.org": "galaxyproject",
    "henning@jacobs1.de": "hjacobs",
    "ian@datagram.co": "boot2docker",
    "ipython-dev@scipy.org": ("ipython", "jupyter-widgets"),
    "jeremy@jeremysanders.net": "veusz",
    "joan@abyz.me.uk": "joan2937",
    "jupyter@googlegroups.com": "jupyter",
    "peak@eby-sarna.com": "PEAK-Legacy",
    "phi@funaba.org": "https://www.funaba.org/code",  # calendar
    "philip@semanchuk.com": "osvenskan",  # sysv_ipc/posix_ipc
    "plaidml-dev@googlegroups.com": "plaidml/plaidml",
    "pygame@pygame.org": "pygame",
    "pypi@tjaart.co.za": "tjaartvdwalt",
    "richard@tartarus.org": "snowballstem",
    "shlomi@smore.com": "smore-inc",
    "smithnick@google.com": "google/{suffix}",  # https://github.com/google/pasta/pull/81
    "support@maxmind.com": "maxmind/{name}-api-python",
    "support@sigopt.com": "sigopt/{name}-python",
    "sympy@googlegroups.com": "sympy",
    "thatch45@gmail.com": "saltstack",
    "tomaz+pypi@tomaz.me": "Yubico/python-{name}",
    "vinay_sajip@red-dove.com": "https://bitbucket.org/vinay.sajip/{name}",
    "vmalloc@gmail.com": "vmalloc",
    "yans@yancomm.net": "zardus",
    "yubico@yubico.com": "Yubico/python-{name}",
}

_namespace_matches = {
    "aliyun": "aliyun/aliyun-openapi-python-sdk",
    "antlr3": "antlr/{namespace}",
    "cognite": "cognitedata",
    "dash": "plotly",
    "dephell": "dephell/dephell_{suffix}",
    "grpcio": (
        "GoogleCloudPlatform/grpc-{suffix}-python",
        "{suffix}-contrib/python-grpc",
        "grpc/grpc",  # should add check for sub-path match of {suffix}(tools, testing, etc)
    ),
    "jupyter": (
        "jupyter",
        "jupyter/jupyter_{suffix}",
        "jupyter/{suffix}",
        "takluyver/jupyter_{suffix}",
        "jdfreder/jupyter-{suffix}",  # jupyter-pip
    ),
    "ipython": "ipython",
    "ipy": ("ipython", "jupyter-widgets"),
    "j1m": "jimfulton/{suffix}",
    "jupyterlab": "jupyterlab",
    "matrix": "matrix-org",  # https://github.com/matrix-org/matrix-synapse-ldap3
    "neptune": "neptune-ai",
    "orange": "biolab",
    "orange3": "biolab",
    "repoze.who.plugins.sa": "repoze/repoze.who-sqlalchemy",
    "repoze": (
        "repoze",
        "repoze/{namespace}.{suffix_parts[0]}-{suffix_parts[2]}",  # repoze.what.plugins.sql -> repoze.what-sql
    ),
    "sphinxcontrib": ("sphinx-doc", "sphinx-contrib"),
    "stsci": "spacetelescope",
    "tg": ("TurboGears", "TurboGears/tg2{suffix}"),
    "tgext": "TurboGears",
    "turbogears2": "Turbogears/tg2/",  # trailing '/' used to only match 'turbogears2', no suffixes
    "xstatic": (
        "openstack",
        "takluyver",
        "xstatic-py",
        "r1chardj0n3s",
        "python-xstatic/{suffix}",
        "dmsimard/{name}-distgit",
        "dmsimard/{suffix}-distgit",
        "dmsimard/python-{name}-distgit",
    ),
    "zc": "zopefoundation",
    "z3c": "zopefoundation",
}


def _find_named_repo(name, emails=None):
    if name.lower() == "xstatic-jquery-ui":
        name = "xstatic-jquery_ui"

    pos_dot = name.find(".")
    pos_dash = name.find("-")
    pos_underscore = name.find("_")
    pos = len(name)
    if pos_dot != -1:
        pos = pos_dot
    if pos_dash != -1 and pos_dash < pos:
        pos = pos_dash
    if pos_underscore != -1 and pos_underscore < pos:
        pos = pos_underscore

    namespace = name[:pos].lower()
    suffix = name[pos + 1 :].lower()

    rules = []
    rule = _namespace_matches.get(name, None)
    if rule:
        if isinstance(rule, str):
            rules.append(rule)
        else:
            rules = list(rule)

    ns_rules = _namespace_matches.get(namespace, [])
    if isinstance(ns_rules, str):
        rules.append(ns_rules)
    else:
        rules += list(ns_rules)

    for email in emails or []:
        address, domain = email.split("@", 1)
        logger.info("email split: {} @ {}".format(address, domain))
        if domain == "lists.sourceforge.net":
            sf_project_name, list_type = address.rsplit("-", 1)
            if list_type in ["bugs", "discuss"]:
                return "https://sourceforge.net/projects/{}".format(sf_project_name)
        elif domain == "lists.freedesktop.org":
            return "https://gitlab.freedesktop.org/{}/{}".format(address, name)

        email_rules = _email_matches.get(email, [])
        if isinstance(email_rules, str):
            email_rules = [email_rules]
        for rule in email_rules:
            if rule not in rules:
                rules.append(rule)

    if not rules:
        return

    logger.info("found repo name rules for {} {}: {!r}".format(name, emails, rules))

    for slug in rules:
        from pypidb._github import check_repo

        if "/" not in slug:
            slug = "{}/{}".format(slug, name)
        elif slug.endswith("/"):
            slug = slug[:-1]
            if namespace != name.lower():
                continue
        else:
            suffix_normalised = normalize(suffix)
            suffix_parts = suffix_normalised.split("-")
            slug = slug.format(
                name=name,
                namespace=namespace,
                suffix=suffix,
                suffix_normalised=suffix_normalised,
                suffix_parts=suffix_parts,
            )

        logger.info("checking {}".format(slug))
        if slug.startswith("https://"):
            return slug
        if check_repo(slug):
            return "https://github.com/{}".format(slug)
