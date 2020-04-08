import os
import os.path
import socket

import requests
from appdirs import user_cache_dir
from cachecontrol import CacheControlAdapter, CacheController
from cachecontrol.caches.file_cache import FileCache
from cachecontrol.heuristics import ExpiresAfter
from logging_helper import setup_logging
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.util.timeout import Timeout

from pypidb import __name__ as app_name
from ._adapters import (
    CDNBlockAdapter,
    ContentTypeBlockAdapter,
    DomainListBlockAdapter,
    HTTPSAdapter,
    IPBlockAdapter,
    LoginBlockAdapter,
    Status500Adapter,
)
from ._compat import urlsplit

try:
    from future.standard_library import install_aliases

    install_aliases()
except ImportError:  # pragma: no cover
    pass

_block_request_adapter = Status500Adapter()
logger = setup_logging()
_CI = os.getenv("CI", "")

MAX_REDIRECTS = 10
retries = 3
backoff_factor = 0.3
status_forcelist = (500, 502, 504)

retry = Retry(
    total=retries,
    read=retries,
    connect=retries,
    backoff_factor=backoff_factor,
    status_forcelist=status_forcelist,
)


def cache_subdir(name):
    dirpath = os.path.join(user_cache_dir(app_name), name)
    return dirpath


def get_timeout(url):
    if "wiki.ros.org" in url or "abyz.me.uk" in url:
        return Timeout(connect=15, read=20, total=45)
    if "svn.eby-sarna.com" in url or "gitorious.org" in url:  # pragma: no cover
        return Timeout(connect=30, read=30, total=60)
    if "w3.org" in url or "pygal.org" in url:
        return Timeout(connect=30, read=30, total=45)
    if not _CI and "galaxyproject.org" in url:
        return Timeout(connect=100, read=100, total=200)

    return Timeout(connect=15, read=11, total=40)


def _check_url_domain(url):
    if "tracpub.yaco.es" in url:  # django-oot
        return True
    if "hg.hardcoded.net" in url:  # sgmllib3k
        return True
    if "github.org" in url:  # tkreadonly
        return True

    try:
        p = urlsplit(url)
    except Exception:
        return False
    if not p.netloc:
        return False
    try:
        socket.gethostbyname(p.netloc)
    except Exception as e:
        logger.info("domain {} lookup error: {}".format(url, e))
        return False
    return True


class IgnoreVaryExpiresAfter(ExpiresAfter):
    def update_headers(self, response):
        headers = super(IgnoreVaryExpiresAfter, self).update_headers(response)
        if "Vary" in response.headers:
            headers["Vary"] = ""
        return headers


class MoreCodesCacheController(CacheController):
    def __init__(
        self, cache=None, cache_etags=True, serializer=None, status_codes=None
    ):
        status_codes = status_codes or (200, 203, 300, 301, 302, 401, 404)
        super(MoreCodesCacheController, self).__init__(
            cache, cache_etags, serializer, status_codes
        )


class ForceTimeoutHTTPAdapter(
    CDNBlockAdapter,
    DomainListBlockAdapter,
    IPBlockAdapter,
    LoginBlockAdapter,
    ContentTypeBlockAdapter,
    HTTPSAdapter,
    CacheControlAdapter,
):
    def __init__(self, *args, **kw):
        timeout = kw.pop("timeout", None)
        super(ForceTimeoutHTTPAdapter, self).__init__(*args, **kw)
        self.timeout = timeout

    def send(self, request, cacheable_methods=None, timeout=None, **kw):
        if self.timeout and not timeout:  # pragma: no cover
            timeout = self.timeout
        return super(ForceTimeoutHTTPAdapter, self).send(request, timeout=timeout, **kw)


class NoVerifyHTTPAdapter(requests.adapters.HTTPAdapter):
    """An HTTP adapter that ignores TLS validation errors. Use at own risk."""

    def cert_verify(self, conn, url, verify, cert):
        super(NoVerifyHTTPAdapter, self).cert_verify(
            conn=conn, url=url, verify=False, cert=cert
        )


def CacheControl(
    sess,
    cache,
    cache_etags=True,
    serializer=None,
    heuristic=None,
    controller_class=None,
    adapter_class=None,
    cacheable_methods=None,
    **kw
):
    assert cache
    adapter_class = adapter_class or CacheControlAdapter
    adapter = adapter_class(
        cache,
        cache_etags=cache_etags,
        serializer=serializer,
        heuristic=heuristic,
        controller_class=controller_class,
        cacheable_methods=cacheable_methods,
        **kw
    )
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)

    sess.mount("ftp://", _block_request_adapter)
    sess.mount("file://", _block_request_adapter)
    sess.mount("irc://", _block_request_adapter)
    sess.mount("wss://", _block_request_adapter)

    sess.mount("http://readme.md/", _block_request_adapter)
    sess.mount("http://license.md/", _block_request_adapter)
    sess.mount("http://contributing.md/", _block_request_adapter)
    sess.mount("http://manifest.in/", _block_request_adapter)
    sess.mount("http://setup.py/", _block_request_adapter)

    sess.mount("http://p01.notifa.info", _block_request_adapter)
    sess.mount("https://p01.notifa.info", _block_request_adapter)
    sess.mount("http://browsehappy.com", _block_request_adapter)
    sess.mount("https://browsehappy.com", _block_request_adapter)
    sess.mount("http://validator.w3.org/check", _block_request_adapter)
    sess.mount("https://validator.w3.org/check", _block_request_adapter)
    sess.mount(
        "http://www.amazon.com/exec/obidos/external-search", _block_request_adapter
    )  # simplegeneric https://github.com/lipoja/URLExtract/issues/62
    sess.mount("https://www.googletagmanager.com/", _block_request_adapter)
    sess.mount("www.google-analytics.com", _block_request_adapter)
    sess.mount("https://www.youtube.com", _block_request_adapter)
    sess.mount("https://youtu.be", _block_request_adapter)

    sess.mount("http://pypistats.org", _block_request_adapter)
    sess.mount("https://pypistats.org", _block_request_adapter)
    sess.mount("http://docs.python.org", _block_request_adapter)
    sess.mount("https://docs.python.org", _block_request_adapter)
    sess.mount("http://www.python.org", _block_request_adapter)
    sess.mount("https://www.python.org", _block_request_adapter)
    sess.mount("http://www.python.org/peps/", _block_request_adapter)
    sess.mount("https://www.python.org/peps/", _block_request_adapter)

    sess.mount("http://www.lfd.uci.edu/~gohlke/pythonlibs", _block_request_adapter)
    sess.mount("https://www.lfd.uci.edu/~gohlke/pythonlibs", _block_request_adapter)

    # Possibly useful, but needs to be used with care
    sess.mount("https://en.wikipedia.org", _block_request_adapter)
    sess.mount("https://packages.debian.org", _block_request_adapter)
    sess.mount("https://mirror.centos.org", _block_request_adapter)
    sess.mount("https://www.openhub.net", _block_request_adapter)  # 'html' package
    sess.mount("https://openhub.net", _block_request_adapter)
    sess.mount("https://www.ohloh.net", _block_request_adapter)
    sess.mount("https://web.archive.org", _block_request_adapter)
    sess.mount("https://badge.fury.io/py/", _block_request_adapter)
    sess.mount("https://www.linkedin.com", _block_request_adapter)
    sess.mount(
        "https://dealbook.nytimes.com", _block_request_adapter
    )  # github-issues-tools; leads to https://github.com/WP-API/WP-API
    sess.mount("http://hub.docker.com", _block_request_adapter)  # cauldron-notebook
    sess.mount("https://hub.docker.com", _block_request_adapter)
    sess.mount("http://docker.com", _block_request_adapter)  # wandb
    sess.mount("https://docker.com", _block_request_adapter)

    # google apps
    sess.mount("https://groups.google.com", _block_request_adapter)
    sess.mount("https://mail.google.com", _block_request_adapter)
    sess.mount("https://docs.google.com/forms/", _block_request_adapter)
    sess.mount(
        "https://docs.google.com/a/datastax.com/forms/", _block_request_adapter
    )  # cassandra-driver

    # Schema
    sess.mount(
        "http://schema.org/", _block_request_adapter
    )  # waiting/readthedocs, wordaxe
    sess.mount("https://schema.org/Article", _block_request_adapter)
    sess.mount("http://ogp.me/ns/", _block_request_adapter)
    sess.mount("https://ogp.me/ns/", _block_request_adapter)
    sess.mount("http://xmlns.com/", _block_request_adapter)
    sess.mount("https://xmlns.com/", _block_request_adapter)
    sess.mount("http://w3.org/TR/", _block_request_adapter)
    sess.mount("http://www.w3.org/TR/", _block_request_adapter)
    sess.mount("https://w3.org/TR/", _block_request_adapter)
    sess.mount("https://www.w3.org/TR/", _block_request_adapter)
    sess.mount("http://w3.org/199", _block_request_adapter)
    sess.mount("http://www.w3.org/199", _block_request_adapter)
    sess.mount("https://w3.org/199", _block_request_adapter)
    sess.mount("https://www.w3.org/199", _block_request_adapter)
    sess.mount("http://w3.org/200", _block_request_adapter)
    sess.mount("http://www.w3.org/200", _block_request_adapter)
    sess.mount("https://w3.org/200", _block_request_adapter)
    sess.mount("https://www.w3.org/200", _block_request_adapter)
    sess.mount("http://w3.org/201", _block_request_adapter)
    sess.mount("http://www.w3.org/201", _block_request_adapter)
    sess.mount("https://w3.org/201", _block_request_adapter)
    sess.mount("https://www.w3.org/201", _block_request_adapter)
    # irc
    sess.mount("http://webchat.freenode.net", _block_request_adapter)
    sess.mount("https://webchat.freenode.net", _block_request_adapter)
    sess.mount("http://irc.freenode.net", _block_request_adapter)
    sess.mount("https://irc.freenode.net", _block_request_adapter)
    sess.mount("http://gitter.im", _block_request_adapter)
    sess.mount("https://gitter.im", _block_request_adapter)
    # licenses
    sess.mount("http://apache.org/licenses/", _block_request_adapter)
    sess.mount("https://apache.org/licenses/", _block_request_adapter)
    sess.mount("http://www.apache.org/licenses/", _block_request_adapter)
    sess.mount("https://www.apache.org/licenses/", _block_request_adapter)
    sess.mount("https://www.creativecommons.org", _block_request_adapter)
    sess.mount("https://creativecommons.org", _block_request_adapter)
    sess.mount("https://wtfpl.net", _block_request_adapter)
    sess.mount("https://opensource.org/licenses/", _block_request_adapter)
    sess.mount("https://www.opensource.org/licenses/", _block_request_adapter)
    sess.mount("https://www.gnu.org/copyleft/", _block_request_adapter)
    sess.mount("https://www.gnu.org/licenses/", _block_request_adapter)
    sess.mount("https://www.gnu.org/philosophy/", _block_request_adapter)
    sess.mount("https://tldrlegal.com", _block_request_adapter)
    # pdf/papers
    sess.mount("https://arxiv.org/", _block_request_adapter)
    sess.mount("http://patft.uspto.gov/netacgi/", _block_request_adapter)  # very slow
    sess.mount("https://patft.uspto.gov/netacgi/", _block_request_adapter)  # BitVector
    sess.mount("http://joss.theoj.org/papers/", _block_request_adapter)  # umap-learn
    sess.mount("http://www.ietf.org/rfc/", _block_request_adapter)

    sess.mount(
        "https://gitter.im/allure-framework/allure-core", _block_request_adapter
    )  # allure-pytest
    sess.mount("https://tracpub.yaco.es", _block_request_adapter)
    sess.mount("http://tracpub.yaco.es", _block_request_adapter)

    # leads to docutils for many projects
    sess.mount("https://sphinx-doc.org", _block_request_adapter)
    sess.mount("http://sphinx-doc.org", _block_request_adapter)
    sess.mount("https://www.sphinx-doc.org", _block_request_adapter)
    sess.mount("http://www.sphinx-doc.org", _block_request_adapter)

    sess.mount("http://www.readthedocs.org", _block_request_adapter)
    sess.mount("https://www.readthedocs.org", _block_request_adapter)
    sess.mount("http://docs.readthedocs.org", _block_request_adapter)
    sess.mount("https://docs.readthedocs.org", _block_request_adapter)
    sess.mount("http://readthedocs.org/projects/", _block_request_adapter)
    sess.mount("https://readthedocs.org/projects/", _block_request_adapter)
    sess.mount("http://readthedocs.org/projects/", _block_request_adapter)
    sess.mount("https://readthedocs.org/projects/", _block_request_adapter)
    sess.mount(
        "https://fedoraproject.org/wiki/Infrastructure/Fedorahosted-retirement",
        _block_request_adapter,
    )
    # CI
    sess.mount("http://travis-ci.org", _block_request_adapter)
    sess.mount("http://travis-ci.com", _block_request_adapter)
    sess.mount("https://travis-ci.org", _block_request_adapter)
    sess.mount("https://travis-ci.com", _block_request_adapter)

    # More distracting than useful
    sess.mount("http://infrae.com", _block_request_adapter)
    sess.mount("https://infrae.com", _block_request_adapter)
    sess.mount(
        "http://peak.telecommunity.com/DevCenter/setuptools", _block_request_adapter
    )

    sess.mount("http://www.blueskyonmars.com", _block_request_adapter)
    sess.mount("https://www.blueskyonmars.com", _block_request_adapter)

    sess.mount("https://gitorious.org", NoVerifyHTTPAdapter())  # oset
    sess.mount("https://gisce.net", NoVerifyHTTPAdapter())  # electrical-calendar

    return sess


def get_file_cache_session(cache_name):
    cache_path = cache_subdir(cache_name)

    https_exceptions = {
        "code.welldev.org",  # pypi oauth_provider; nothing on https; http is parked
        "fedmsg.com",  # https redirects to http, causing too-many-redirects
        "farmdev.com",  # SSL_ERROR_RX_RECORD_TOO_LONG
        "abyz.me.uk",  # expired pigpio
        "api.arduino.cc",
        "cdn.arduino.cc",  # rpi-gpio
        "lamb.cc",  # script
        # https very slow:
        "pybrary.net",
        "fabfile.org",  # port 80 also timing out
        "paramiko.org",  # port 80 also timing out
        "pyinvoke.org",  # port 80 also timing out
        "www.freecell.org",
        "www.dnspython.org",
        "stutzbachenterprises.com",
        "blockdiag.com",
        "welbornprod.com",  # :80 redirects to github
        "code.krypto.org",  # hashlib
        "intelligent-systems.altran.com",  # spark-parser
        "dalkescientific.com",  # PyRSS2Gen
        "luispedro.org",  # pymorph
        "dir.gmane.org",  # dm.xmlsec-binding
        "bibframe.org",  # pybibframe
        "galaxyproject.org",  # galaxy
        # nothing on https:
        "www.mypy-lang.org",
        "www.decida.org",
        "www.alcyone.com",
        "www.aaronsw.com",
        "whitemans.ca",
        "www.roundup-tracker.org",
        "code.mibian.net",
        "peak.telecommunity.com",
        "www.ruffus.org.uk",
        "kaino.kotus.fi",
        "wordlist.aspell.net",
        "www.python-excel.org",
        "sparrow.telecommunity.com",
        "blog.pediapress.com",
        "eh.org",
        "www.linuxrising.org",  # pygtk
        "www.4guysfromrolla.com",
        "svn.eby-sarna.com",
        "azure.archive.ubuntu.com",  # blurb
        "www.should-dsl.info",  # should_dsl
        "cvs.bigasterisk.com",  # pyalsa
        "decida.org",  # DeCiDa
        "antirez.com",  # redlock-py
        "docs.h2o.ai",  # https://github.com/h2oai/sparkling-water/issues/1953
        "www.theblobshop.com",  # https://github.com/jmyounker/vers/issues/1
        # wrong cert
        "pybrain.org",  # cert for *.kasserver.com, kasserver.com (unrelated)
        "www.unnotebook.com",  # cloudfront.net, *.cloudfront.net
        "download.ros.org",  # *.osuosl.org
        "fimi.ua.ac.be",  # pyfim
        "kassiopeia.juls.savba.sk",  # unicode; errkorp.juls.savba.sk
        "www.hackersdelight.org",  # *.ipower.com
        "download.qt-project.org",  # *.qt.io
        "occiput.scienceontheweb.net",  # petlink
        "morpho.aalto.fi",  # Morfessor
        "www.anderoid.com",  # BitVector
        "urlgrabber.baseurl.org",  # beaverbarcamp.org, www.beaverbarcamp.org
        "celljam.net",  # *.webfaction.com, webfaction.com
        "www.acooke.org",  # *.webfaction.com, webfaction.com
        "timgolden.me.uk",  # *.webfaction.com, webfaction.com
        "mpmath.org",  # *.webfaction.com, webfaction.com
        "www.myhdl.org",  # *.webfaction.com, webfaction.com
        "science.webhostinggeeks.com",  # webhostinggeeks.com, www.webhostinggeeks.com
        "sphinx.pocoo.org",  # pocoo.org, www.pocoo.org
        "lists.baruwa.org",  # *.baruwa.net, baruwa.net
        "yum.baseurl.org",  # beaverbarcamp.org
        "python-tmx.nongnu.org",  # www.gnu.org and friends
        "cthedot.de",  # *.mivitec.net
        "www.acoular.org",  # *.webgo24.de
        "bibfra.me",  # *.library.link
        "www.grantjenks.com",  # https://github.com/grantjenks/python-diskcache/issues/141
        "www.nomadblue.com",  # *.herokuapp.com
        "www.likit.lt",  # ebcdic, *.serveriai.lt
        "www.jsnp.net",  # magic
        "demo.drfdocs.com",  # cert github
        "spockframework.org",  # github
        "schemaform.io",  # github
        "octopress.org",  # github
        "augeas.net",  # github
        "blog.myrhy.me",  # github
        "mypaint.org",  # github, pygtyk
        "www.cheetahtemplate.org",  # github
        "www.keyczar.org",  # redirects to github, hosted by shortener.secureserver.net
        "nltk.org",  # redirects to docs site, hosted by shortener.secureserver.net
        "pynag.org",
        "trivas.pl",
        "psychtoolbox.org",
        "app.datarobot.com",
        "modestmaps.com",  # github
        #'geopandas.org',  # cert github fails https://github.com/geopandas/geopandas/issues/1287
        #'pysolar.org',  # cert github fails
        "www.pyqtgraph.org",  # cert github fails
        "www.buildout.org",
        "docs.buildout.org",  # *.readthedocs.io, readthedocs.io
        "babel.pocoo.org",  # *.readthedocs.io, readthedocs.io
        "www.zodb.org",  # *.readthedocs.io, readthedocs.io
        "www.pygal.org",
        "cloudbridge.cloudve.org",  # readthedocs
        "www.getlfs.com",  # cert wrong host
        "demo.getlfs.com",  # www.holz-hoehne.de
        "docs.getlfs.com",  # rtd
        "git.tremily.us",  # blog.tremily.us
        "gfxmonk.net",  # https://github.com/timbertson/termstyle/issues/10
        # self signed
        "www.larryhastings.com",  # self signed
        "github-api.hive.pt",  # self signed
        "www.goof.com",  # BitVector
        # www.modwsgi.org special case redirects to rtd
        "konlpy.org",  # *.readthedocs.org, readthedocs.org
        "deeplearning.net",  # expired
        "www.beian.gov.cn",  # expired
        "www.functx.com",
        "lists2.idyll.org",  # bad cert
        # ID tracker
        "p01.notifa.info",
        # indirect
        "api.del.icio.us",  # pyalsa; hostname 'api.del.icio.us' doesn't match either of '*.pinboard.in', 'pinboard.in'
        # ok in Firefox, but cert verify failed
        "www.dabeaz.com",  # This server supports TLS 1.0 and TLS 1.1.  This server's certificate chain is incomplete.
        "html5up.net",
        "pages.cpsc.ucalgary.ca",  # https://www.ssllabs.com/ssltest/analyze.html?d=pages.cpsc.ucalgary.ca&latest
        "www.thevirtualbrain.org",
        "web.resource.org",
        "zesty.ca",
    }

    base = os.path.dirname(__file__)

    session = requests.Session()
    session = CacheControl(
        session,
        cache=FileCache(cache_path),
        controller_class=MoreCodesCacheController,
        adapter_class=ForceTimeoutHTTPAdapter,
        cacheable_methods=("GET"),  # https://github.com/ionrock/cachecontrol/issues/216
        heuristic=IgnoreVaryExpiresAfter(days=5),
        blocklist=os.path.join(base, "park_providers.txt"),
        https_exceptions=https_exceptions,
    )
    session.max_redirects = MAX_REDIRECTS

    if cache_name == "web":
        session.mount("http://pypi.org", _block_request_adapter)
        session.mount("https://pypi.org", _block_request_adapter)
        session.mount("http://pypi.python.org", _block_request_adapter)
        session.mount("https://pypi.python.org", _block_request_adapter)
        session.mount("http://cheeseshop.python.org", _block_request_adapter)
        session.mount("https://cheeseshop.python.org", _block_request_adapter)
        session.mount("http://UNKNOWN", _block_request_adapter)
        session.mount("https://UNKNOWN", _block_request_adapter)

    return session


get_file_cache = get_file_cache_session
