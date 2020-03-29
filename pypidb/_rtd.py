import os

from cachetools import cached, LRUCache
from logging_helper import setup_logging

from ._auth import _get_token
from ._cache import get_file_cache
from ._compat import urlsplit
from ._github import check_repo

logger = setup_logging()

session = get_file_cache("rtd")

TOKEN = os.environ.get("RTD_AUTH_TOKEN")
logger.debug("TOKEN: {}".format(TOKEN))
headers = {}
if TOKEN:
    headers["Authorization"] = "Token {}".format(TOKEN)


class AuthenticationError(Exception):
    pass


class ReadtheDocs:
    def __init__(self, base_url="https://readthedocs.org/api/v3/"):
        self.headers = headers
        self.base_url = base_url
        token = _get_token("readthedocs.io")
        if token:
            self.headers["Authorization"] = "Token {}".format(TOKEN)

    def base(self):
        """Simple query just to check connection"""
        return session.get(self.base_url)

    @cached(cache=LRUCache(maxsize=12))
    def get_project(self, name, version=None):
        if "/v2/" in self.base_url:
            url = "{}footer_html/?format=json&project={}&version=v{}".format(
                name, version
            )
        else:
            url = "{}projects/{}".format(self.base_url, name)
        logger.debug("rtd request: {}".format(url))
        response = session.get(url, headers=self.headers)
        logger.debug(response.headers)
        try:
            data = response.json()
        except Exception as e:
            logger.error("get_project: {}".format(e))
            return

        if data == {"detail": "Invalid token."}:
            raise AuthenticationError("Invalid token")

        logger.debug("rtd {}: {}".format(name, data))

        repo = data.get("repository")
        logger.info(repo)

        if not repo:
            return

        url = repo.get("url")
        return url


@cached(cache=LRUCache(maxsize=12))
def _get_repo_v2_footer(name, version="latest", dot_com=True):
    url = "https://readthedocs.{}/api/v2/footer_html/?format=json&project={}&version={}&page=index&docroot=/&source_suffix=.rst"
    url = url.format("com" if dot_com else "org", name, version)

    response = session.get(url)
    logger.debug(
        "rtd v2: {} {} {} {}".format(name, response, response.headers, response.content)
    )
    try:
        data = response.json()
    except Exception as e:
        logger.error("rtd v2: {}".format(e))
        return

    html = data.get("html")
    if not html:
        return

    pos = html.find('"https://github.com/')
    if pos == -1:
        pos = html.find('"https://bitbucket.org')
    if pos == -1:
        return
    html = html[pos + 1 : pos + 100]
    end = html.find("/blob/")
    if end == -1:
        end = html.find("/src/")
    url = html[:end]
    return url


def get_repo(slug, version="latest", dot_com=None, v2=None, strip_docs_suffix=True):
    if "://" in slug:
        p = urlsplit(slug)
        path = p.path
        if path:
            path = p.path[1:]

        host_parts = p.netloc.split(".")
        if len(host_parts) == 3:
            subdomain, _, hostname = p.netloc.partition(".")
            if subdomain in ["docs"]:
                return
            if hostname == "readthedocs-hosted.com":
                dot_com = True
            if path:
                try:
                    lang, version, _ = path.split("/", 2)
                except ValueError:
                    logger.info("rtd Couldnt split {}".format(path))
        else:
            assert len(host_parts) == 2, "{} unknown".format(host_parts)
            assert host_parts[0] == "readthedocs"
            assert path.startswith("projects/"), "{} unknown".format(path)
            try:
                _, subdomain, _ = path.split("/", 2)
            except ValueError:
                logger.info("rtd Couldnt split {}".format(path))
    else:
        subdomain = slug

    if subdomain in ["docs", "www", "assets"]:
        return

    if subdomain in ["python-jsonschema-objects"]:
        v2 = True

    url = None
    if not dot_com and not v2:
        rtd = ReadtheDocs()
        try:
            url = rtd.get_project(subdomain)
        except AuthenticationError:
            pass

    if not url:
        url = _get_repo_v2_footer(subdomain, version, dot_com)

    if not url:
        return

    if url.endswith(".git"):
        url = url[:-4]

    if url.startswith("git://"):
        url = "https://{}".format(url[6:])
    elif url.startswith("http://"):
        url = "https://github.com" + url[len("http://github.com") :]

    if url == "https://github.com/zzzeek/redirectthedocs":
        return

    if strip_docs_suffix:
        docless_url = None
        if url.endswith("-docs"):
            docless_url = url[:-5]
        elif url.endswith("doc"):
            docless_url = url[:-3]
        elif url.endswith("docs"):
            docless_url = url[:-4]
        elif url.endswith("/docs"):
            docless_url = url[:-5]
        elif url.endswith("/documentation"):
            docless_url = url[: len("/documentation")]
        elif url.endswith("/devguide"):  # CPython
            return
        elif url.endswith("/packaging.python.org"):
            return
        elif url.endswith("/pypa.io"):  # certifi
            return

        if docless_url and "github.com" in docless_url:
            if check_repo(docless_url):
                return docless_url

    return url
