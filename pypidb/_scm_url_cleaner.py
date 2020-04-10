import logging
from functools import partial

from cachetools import cached, LRUCache
from logging_helper import setup_logging

from ._cache import get_file_cache
from ._compat import PY2, logger_helper, parse_qs, urlsplit
from ._lp import _launchpad
from ._pagure import _pagure_io
from ._rtd import get_repo as _rtd_get_repo

logger = setup_logging()
if logger_helper and not PY2:
    autolog = logger_helper.LoggerHelper(logging.getLogger(__name__), logging.DEBUG)
else:  # pragma: no cover
    autolog = lambda x: x


def _match_hostname(url, condition, require_path=None, require_no_path=False):
    """require_path defaults to True unless match_subdomains is enabled."""
    scheme, _, other = url.partition(":")
    if scheme not in (
        "git",  # lxc-python2
        "git+https",  # asyncssh
        "http",
        "https",
        "svn",  # wsgiref
    ):
        return False

    if condition.startswith("http://"):
        condition = condition[7:]

    hostname, _, path = condition.partition("/")
    if ":" in hostname:
        hostname = hostname.split(":", 1)[0]

    if "." not in other:  # pragma: no cover
        return False  # '/dev/' in http://www.reportlab.com/

    other = other.lstrip("/")
    match_subdomains = hostname.startswith("*.")
    if match_subdomains:
        hostname = hostname[2:]

        subdomain, other = other.split(".", 1)
        if subdomain in ["www"]:
            logger.debug("url {} subdomain www".format(url))
            return False
    if not other.startswith(hostname):
        return None

    if require_path is None:
        require_path = not match_subdomains

    # Require at least a suffix
    other = other[len(hostname) :]
    other = other.lstrip("/")
    if not other:
        if require_no_path:
            return True

        if require_path:
            logger.debug("url {} no path".format(url))
            return False

    if path:
        if not other.startswith(path):
            logger.debug("url {} not path {}".format(url, path))
            return False

    return True


def _first_two_path(url):
    p = urlsplit(url)

    owner = p.path[1:]
    owner, _, other = owner.partition("/")
    repo, _, other = other.partition("/")

    if not owner or not repo:
        return

    return (owner, repo)


def _skip_x_path(url, skip=0, include_hostname=False, prefix=None):
    p = urlsplit(url)

    path = p.path[1:]
    while skip:
        _, _, path = path.partition("/")
        skip -= 1

    owner, _, path = path.partition("/")
    repo, _, other = path.partition("/")

    if not prefix:
        prefix = owner

    if include_hostname:
        return "https://{}/{}/{}".format(p.netloc, prefix, repo)
    else:
        return prefix, repo


def _skip_one_path(url, owner=None, hostname=None, scheme="https"):
    p = urlsplit(url)

    path = p.path[1:]
    if not path:
        return

    # Skip next 'foo/' in path
    _, _, path = path.partition("/")
    if not owner:
        owner, _, path = path.partition("/")

    repo, _, _ = path.partition("/")
    if hostname:
        return "{}://{}/{}/{}".format(scheme, hostname, owner, repo)

    return owner, repo


def _add_first_path(url, owner=None, hostname=None):
    p = urlsplit(url)

    path = p.path[1:]
    repo, _, other = path.partition("/")
    if hostname:
        return "https://{}/{}/{}".format(hostname, owner, repo)
    else:
        return (owner, repo)


def _hostname(url):
    p = urlsplit(url)
    return "https://{}/".format(p.netloc)


def _hostname_first_path(url):
    p = urlsplit(url)

    path = p.path[1:]
    repo, _, other = path.partition("/")
    return "https://{}/{}".format(p.netloc, repo)


def _hostname_two_paths(url, scheme="https", hostname=None, trailing=""):
    p = urlsplit(url)

    path = p.path[1:]
    path1, _, other = path.partition("/")
    path2, _, other = other.partition("/")
    if not path1 or not path2:
        return
    if not hostname:
        hostname = p.netloc
    return "{}://{}/{}/{}{}".format(scheme, hostname, path1, path2, trailing)


def _hostname_three_paths(url):
    p = urlsplit(url)

    path = p.path[1:]
    path1, _, other = path.partition("/")
    path2, _, other = other.partition("/")
    path3, _, other = other.partition("/")
    if not path1 or not path2 or not path3:  # pragma: no cover
        return
    return "https://{}/{}/{}/{}".format(p.netloc, path1, path2, path3)


def _subdomain_to_path(url, hostname=None, prefix=None, exclude=[], append_part=None):
    p = urlsplit(url)
    subdomain, _, domain = p.netloc.partition(".")
    if not hostname:
        hostname = domain
    if subdomain in exclude:
        return
    suffix = ""
    if append_part:
       if p.path[0] != "/":
           return
       parts = p.path[1:].split("/")
       suffix = "/" + parts[append_part - 1]
    if prefix:
        return "https://{}/{}{}{}".format(hostname, prefix, subdomain, suffix)
    return "https://{}/{}{}".format(hostname, subdomain, suffix)  # pragma: no cover


def _ghbtns(url):
    p = urlsplit(url)
    q = p.query
    if not p:  # pragma: no cover
        return
    params = parse_qs(q)
    if "user" not in params or "repo" not in params:
        return
    return params["user"][0], params["repo"][0]


def _subdomain_to_github(owner, url, exclude=[]):
    p = urlsplit(url)
    repo = p.netloc.split(".")[0]
    if repo in exclude:
        return False
    if (owner, repo) == ("apache", "qpid"):
        path = p.path
        if not path:  # pragma: no cover
            return
        path = path[1:]
        if not path:  # pragma: no cover
            return
        subproject, _, other = path.partition("/")
        if not subproject:  # pragma: no cover
            return
        repo = repo + "-" + subproject
    return (owner, repo)


def _github_io(url):
    p = urlsplit(url)
    owner = p.netloc.split(".")[0]
    logger.debug("_github_io {} {}".format(url, owner))
    if owner in [
        "api",
        "avatars",
        "buttons",  # plaidml-keras
        "developer",
        "enterprise",
        "help",
        "gist",
        "nodeload",
        "training",
        "user-images",
        "www",
    ]:
        return False
    path = p.path[1:]
    if not path:
        return
    repo, _, _ = path.partition("/")
    if not repo:  # pragma: no cover
        return
    # https://github.com/lipoja/URLExtract/issues/62#issuecomment-609275267
    if repo == "&":
        return
    if (owner, repo) in [("smartsheet-platform", "api-docs")]:
        return
    return (owner, repo)


def _strip_dot_git(url):
    pos = url.find(".git")
    if pos == -1:
        return url
    return url[:pos]


def _strip_after_dot_git(url):
    pos = url.find(".git")
    if pos == -1:
        return url
    return url[: pos + 4]


def _linaro_org(url):
    if "/git/" in url:
        return "https://git.linaro.org/{}/{}".format(*_skip_one_path(url))
    return url


def _all(url):
    return url


def _reject(url):
    return False


def _get_redirect_location(url):
    web_session = get_file_cache("web")
    if url.startswith("git+"):
        url = url[4:]
    r = web_session.get(url, allow_redirects=False)
    r.raise_for_status()
    assert "location" in r.headers
    assert r.headers["location"]
    url = r.headers["location"]
    if "opendev.org" in url and url.endswith("/"):
        url = url[:-1]
    return url


def _follow_rtd_get_repo(url):
    try:
        url = _get_redirect_location(url)
    except Exception:
        pass

    return _rtd_get_repo(url)


def _google_code(url):
    p = urlsplit(url)

    logger.debug("google code {}".format(url))

    if p.netloc == "issuetracker.google.com" and p.path.startswith("/code/"):
        p = urlsplit("https://code.google.com/" + p.path[6:])

    if p.netloc == "code.google.com":
        path = p.path[1:]
        if not path:  # pragma: no cover
            return
        part1, _, other = path.partition("/")

    else:
        url = _subdomain_to_path(url, prefix="p/", hostname="code.google.com")
        logger.debug("google code subdomain -> {}".format(url))
        p = urlsplit(url)

        path = p.path[1:]
        if not path:  # pragma: no cover
            return
        part1, _, other = path.partition("/")

    logger.debug("google code {} {}".format(part1, other))

    if part1 == "archive":
        part1, _, other = other.partition("/")

    if part1 == "a":
        return "https://code.google.com/a/{}".format(other)
    assert part1 == "p"
    project, _, other = other.partition("/")

    url = "https://code.google.com/p/{}".format(project)

    try:
        redirect = _get_redirect_location(url)
        if "code.google.com" not in redirect:
            return redirect
    except AssertionError:
        pass

    return url


def _telecommunity(url):
    if "setuptools" not in url:
        return _skip_one_path(hostname="svn.eby-sarna.com", scheme="http", url=url)


def _bitbucket(url):
    if url.startswith("https://drone.io/"):
        url = url = "https://" + url[len("https://drone.io/") :]

    url = _hostname_two_paths(url, hostname="bitbucket.org")
    if not url:
        return url

    try:
        web_session = get_file_cache("web")
        r = web_session.get(url, allow_redirects=False)
        content = r.content.decode("utf-8")
    except Exception as e:
        logger.info("bitbucket error {}".format(e))
        return url

    try:
        pos = content.find('It now lives at <a href="')
        if pos == -1:
            return url

        pos += len('It now lives at <a href="')
        end = content.find('"', pos)
        url = content[pos:end]
        logger.info("bitbucket redirecting to {}".format(url))
        url = url.replace(
            "https://sourceforge.net/p/", "https://sourceforge.net/projects/"
        )
    except Exception as e:
        logger.info("bitbucket error {}".format(e))
        raise

    if url.startswith("http://github.com"):
        url = url.replace("http://", "https://")
    elif url.startswith("https://sourceforge.net") and url[-1] == "/":
        url = url[:-1]
    elif url.startswith("https://hg.anteru.net") and url[-1] == "/":
        url = url[:-1]

    return url


def _zope_svn(url):
    p = urlsplit(url)
    if not p.path:  # pragma: no cover
        return False
    path = p.path.strip("/")
    if not path:  # pragma: no cover
        return False
    parts = path.split("/")
    if not parts:  # pragma: no cover
        return False
    name = parts[0]
    if not name:  # pragma: no cover
        return False
    if name == "zc.buildout":
        return ("buildout", "buildout")
    else:
        return ("zopefoundation", name)


def _gitlab(url, hostname=None):
    p = urlsplit(url)

    path = p.path[1:]
    if not path:  # pragma: no cover
        return
    if path.startswith("assets/"):
        return

    owner, _, path = path.partition("/")

    if not path:
        return
    for action in ["issues", "badges", "merge_requests"]:
        pos = path.find("/" + action)
        if pos != -1:
            path = path[:pos]
            break

    if not hostname:
        hostname = p.netloc
    return hostname, owner, path


_gitea = _hostname_two_paths  # gitea doesnt support groups


@autolog
def _github(url):
    try:
        rv = _first_two_path(url)
    except Exception as e:  # pragma: no cover
        logger.info("github split: {}".format(e))
        return False

    if not rv:
        return False
    owner, repo = rv

    if not owner or not repo:
        return False
    if owner in ["site", "users", "notifications", "customer-stories-feed"]:
        return False

    trimmed_repo, _, ext = repo.partition(".")
    if ext in ["git", "wiki"]:
        repo = trimmed_repo

    if (owner, repo) in [
        ("apache", "httpd"),  # pyside2
        ("reeset", "data_packs"),  # pybibframe
        ("typesafehub", "config"),  # strictyaml
        ("lightbend", "config"),  # strictyaml
        ("biolab", "orange"),  # https://github.com/biolab/orange3/pull/4344
        ("smartsheet-platform", "api-docs"),
    ]:
        return

    return owner, repo


_sf_rejects = [
    "apps",  # sf internal
    "djvu",  # python-djvulibre
    "lists",
    "ntlmaps",  # repoze.sphinx.autointerface
    "tidy",  # pytidylib
    "www",
]


def _sf(url):
    url = url.replace("sf.net", "sourceforge.net")

    if "turbogears1" in url:
        return url

    p = urlsplit(url)

    path = p.path[1:]

    if p.netloc == "lists.sourceforge.net":
        if path.startswith("lists/listinfo/"):
            list_name = path[len("lists/listinfo/") :]
        elif path.startswith("mailman/listinfo/"):
            list_name = path[len("mailman/listinfo/") :]
        else:
            assert False, path
        project_name = ""
        if list_name.endswith("-discuss"):
            project_name = list_name[: -len("-discuss")]
        if project_name:
            return "https://sourceforge.net/projects/{}".format(project_name)
        return
    elif p.netloc in ["sourceforge.net", "sf.net", "sourceforge.jp"]:
        if path in ["project/platformdownload.php", "project/showfiles.php"]:  # wordaxe
            url = _get_redirect_location(url.replace("http:", "https:"))
            p = urlsplit(url)
            path = p.path[1:]
    elif ".code." in p.netloc:
        pass
    else:
        subdomain = p.netloc
        subdomain = subdomain.replace(".sourceforge.net", "")
        subdomain = subdomain.replace(".sf.net", "")
        subdomain = subdomain.replace(".sourceforge.jp", "")
        logger.info("sf subdomain {} of {}".format(subdomain, url))
        if "." not in subdomain and subdomain not in _sf_rejects:
            return "https://sourceforge.net/projects/{}".format(subdomain)

    try:
        url = _skip_one_path(url, owner="projects", hostname="sourceforge.net")
    except Exception as e:  # pragma: no cover
        logger.warning("_sf exception: {}".format(e))
        return

    if not url:  # pragma: no cover
        logger.info("sf no url {}".format(url))
        return

    if not path:  # pragma: no cover
        logger.info("sf no path in {}".format(url))
        return

    name = url.rsplit("/", 1)[1]
    if not name:
        return False

    if name in _sf_rejects:
        logger.info("sf rejected {} in {}".format(name, _sf_rejects))
        return

    logger.info("accepted {} not in {}".format(name, _sf_rejects))

    return url


class SCMURLCleaner(object):
    fixers = {
        "raw.githubusercontent.com/": _first_two_path,
        "github.com": _github,
        "api.github.com/repos/": _skip_one_path,  # google-api-core
        "wiki.github.com": _first_two_path,  # pybrain
        "github.org": _github,  # tkreadonly, coverage-reporter
        "www.github.com": _github,
        "raw.github.com": _github,
        "travis-ci.org": _github,
        "travis-ci.com": _github,
        "www.travis-ci.org": _github,  # civisml-extensions
        "api.travis-ci.org": _github,
        "api.travis-ci.com": _github,
        "secure.travis-ci.org": _github,
        "bitbucket.org": _bitbucket,
        "www.bitbucket.org": _bitbucket,
        "gitlab.com": _gitlab,
        "www.gitlab.com": _gitlab,
        "rate.re/github/": _skip_one_path,  # docxtpl
        "codecov.io/gh/": _skip_one_path,
        "codecov.io/github/": _skip_one_path,
        "coveralls.io/github/": _skip_one_path,
        "coveralls.io/repos/github/": partial(_skip_x_path, skip=2),
        "coveralls.io/r/": _skip_one_path,
        "codeclimate.com/github/": _skip_one_path,
        "app.shippable.com": _skip_one_path,  # These should include /github
        "circleci.com/gh/": _skip_one_path,
        "nbviewer.jupyter.org/github/": _skip_one_path,
        "drone.io/bitbucket.org/": _bitbucket,
        "ci.appveyor.com/api/projects/status/github/": partial(_skip_x_path, skip=4),
        "requires.io/github/": _skip_one_path,
        "pyup.io/repos/github/": partial(_skip_x_path, skip=2),
        "img.shields.io/appveyor/ci/": partial(_skip_x_path, skip=2),
        "img.shields.io/codecov/c/github/": partial(_skip_x_path, skip=3),
        "img.shields.io/github/commit-activity/y/": partial(_skip_x_path, skip=3),
        "img.shields.io/github/license/": partial(_skip_x_path, skip=2),
        "img.shields.io/lgtm/alerts/g/": partial(_skip_x_path, skip=3),
        "img.shields.io/lgtm/grade/python/g/": partial(_skip_x_path, skip=4),
        "img.shields.io/travis/": _skip_one_path,
        "lgtm.com/projects/g/": partial(_skip_x_path, skip=2),
        "ghbtns.com/github-btn.html?": _ghbtns,
        "github.enthought.com/": partial(
            _add_first_path, owner="enthought"
        ),  # https://github.com/enthought/ets/issues/28
        "ssbjenkins.stsci.edu/job/STScI/job/": partial(
            _skip_x_path, skip=2, prefix="spacetelescope"
        ),
        "launchpad.net/": _launchpad,
        "www.launchpad.net/": _launchpad,
        "answers.launchpad.net/": _launchpad,
        "bazaar.launchpad.net/": _launchpad,
        "blueprints.launchpad.net/": _launchpad,
        "bugs.launchpad.net/": _launchpad,
        "code.launchpad.net/": _launchpad,
        "feeds.launchpad.net/": _launchpad,
        "translations.launchpad.net/": _launchpad,
        "pagure.io": _pagure_io,
        "savannah.gnu.org/projects/": _hostname_two_paths,
        "git.savannah.gnu.org/cgit/": _all,  # todo rewrite to savannah.gnu.org
        "git.sv.gnu.org": partial(
            _add_first_path, owner="projects", hostname="savannah.gnu.org"
        ),
        "savannah.nongnu.org/projects/": _hostname_two_paths,
        "sourceforge.net/project/platformdownload.php?group_id=": _sf,
        "sourceforge.net/project/showfiles.php?group_id=": _sf,
        "sourceforge.net/projects/": _sf,
        "sourceforge.jp/projects/": _sf,
        "sourceforge.net/p/": _sf,
        "apps.sourceforge.net/trac/": _sf,  # rewrite to sf.net/projects/
        "lists.sourceforge.net/lists/listinfo/": _sf,  # Cheetah
        "*.code.sourceforge.net/p/": _sf,
        "*.code.sf.net/p/": _sf,
        "sf.net/projects/": _sf,
        "*.sourceforge.net": _sf,
        "*.sf.net": _sf,
        # https://github.com/jayvdb/pypidb/issues/46
        "softwarefactory-project.io/r/": partial(
            _skip_x_path,
            skip=0, include_hostname=True, prefix="cgit",
        ),  # logreduce
        "*.softwarefactory-project.io": partial(
            _subdomain_to_path, prefix="cgit/"
        ),  # logreduce
        "softwarefactory-project.io/cgit/": _hostname_two_paths,
        "www.logilab.org/project/": _hostname_two_paths,
        "git-wip-us.apache.org/repos/": _all,
        "gitbox.apache.org/repos/": _all,
        "*.apache.org": partial(
            _subdomain_to_github,
            "apache",
            exclude=[
                "blogs",
                "community",
                "dist",
                "donate",
                "git-wip-us",
                "gitbox",
                "helpwanted",
                "httpd",
                "incubator",
                "issues",
                "jakarta",
                "labs",
                "people",
                "projects",
                "s",
                "status",
                "www",
            ],
        ),
        "pygobject.readthedocs.io": lambda url: "https://gitlab.gnome.org/GNOME/pygobject",
        "readthedocs.io/projects/": _rtd_get_repo,
        "readthedocs.org/projects/": _rtd_get_repo,
        "readthedocs.com/projects/": _rtd_get_repo,
        "*.readthedocs.io": _rtd_get_repo,
        "*.readthedocs.org": _rtd_get_repo,
        "*.readthedocs.com": _rtd_get_repo,
        "*.rtfd.org": _rtd_get_repo,
        "*.rtfd.io": _rtd_get_repo,
        "*.readthedocs-hosted.com": _follow_rtd_get_repo,
        "*.github.io": _github_io,
        "*.github.com": _github_io,
        "githubapi.com": _first_two_path,  # PyPI 'python-github' unaffiliated broken website
        "gitorious.org": _all,
        "gitorious.com": _all,
        "svn.turbogears.org": lambda url: "https://sourceforge.net/projects/turbogears1",
        "docs.turbogears.org/Turbo": lambda url: "https://sourceforge.net/projects/turbogears1",
        "docs.turbogears.org/tg": lambda url: "https://sourceforge.net/projects/turbogears1",
        "mercurial-scm.org/release/": lambda url: "https://www.mercurial-scm.org/repo/hg",
        "svn.timgolden.me.uk/wmi/trunk": lambda url: "https://github.com/tjguk/wmi",
        "dev.louiz.org/projects/slixmpp": lambda url: "https://lab.louiz.org/poezio/slixmpp",
        "docs.celeryproject.org/projects/": partial(
            _skip_one_path, owner="celery"
        ),  # This should translate second to https://github.com/celery/
        "docs.releng.linuxfoundation.org/projects/lftools": lambda url: "https://gerrit.linuxfoundation.org/infra/q/project:releng%252Flftools",
        "gerrit.linuxfoundation.org": _all,
        "code.google.com/a/": _google_code,
        "code.google.com/archive/a/": _google_code,
        "code.google.com/p/": _google_code,
        "code.google.com/archive/p/": _google_code,
        "issuetracker.google.com/p/": _google_code,
        "*.googlecode.com": _google_code,
        "git.openstack.org": _get_redirect_location,
        "gitlab.gnome.org": _gitlab,
        "foss.heptapod.net": _gitlab,
        "git.nzoss.org.nz": _gitlab,  # detect-delimiter
        "code.qt.io/cgit/": _strip_after_dot_git,
        "gitlab.freedesktop.org": _gitlab,
        "*.freedesktop.org/releases/": partial(
            _subdomain_to_path,
            hostname="gitlab.freedesktop.org",
            append_part=2,
        ),  # dbus-python
        "cgit.freedesktop.org/wiki/": _reject,
        "cgit.freedesktop.org": _hostname_two_paths,
        "git.tuxfamily.org/gitroot": _reject,
        "git.tuxfamily.org": _strip_after_dot_git,
        "salsa.debian.org": _all,
        "git.fmrib.ox.ac.uk": _gitlab,
        "gitlab.math.univ-paris-diderot.fr": _gitlab,
        "git.tremily.us/?p=": _strip_after_dot_git,  # also git://tremily.us/igor.git
        "hg.python.org/lookup": _reject,
        "hg.python.org/tracker": _hostname_two_paths,
        "hg.python.org": _hostname_first_path,
        "www.mercurial-scm.org/repo/hg": _all,
        "svn.python.org/projects/": _hostname_two_paths,
        "svn.zope.org": _zope_svn,
        "hg.tryton.org": _hostname_first_path,
        "*.tryton.org": partial(_subdomain_to_path, hostname="hg.tryton.org"),
        "hg.jcea.es": _hostname_first_path,
        "hg.hardcoded.net": _hostname_first_path,
        "hg.sschwarzer.net": _hostname_first_path,
        "*.sschwarzer.net": _hostname,
        "hg.mozilla.org": _all,
        "www.riverbankcomputing.com/hg/": _hostname_two_paths,
        "www.riverbankcomputing.com/software/": _hostname_two_paths,
        "hg.logilab.org": _gitlab,  # roughly correct
        "hg.piranha.org.ua": _hostname_first_path,
        "hg.anteru.net": _hostname_first_path,
        "www.tablix.org/~avian/git/": partial(
            _skip_x_path, skip=4, include_hostname=True
        ),  # Unidecode & publicsuffix are here, but they use GitHub now
        "yum.baseurl.org/gitwebd27a.html?p=": _strip_dot_git,
        "yum.baseurl.org/gitweb?p=": _strip_dot_git,
        "opendev.org": _gitea,
        "yourlabs.io": _gitlab,
        "gitlab.kitware.com": _gitlab,
        "git.cornhooves.org": _gitlab,
        "gitlab.lis-lab.fr": _gitlab,
        "forge-2.ircam.fr": _gitlab,  # pysndfile
        "www.graphics.rwth-aachen.de:9000": _hostname_two_paths,
        "www.saddi.com/software/": partial(_hostname_two_paths, trailing="/"),
        # svn.saddi.com': _hostname_first_path,
        "svn.hepforge.org": _hostname_first_path,  # 404 pyfeyn
        "http://peak.telecommunity.com/DevCenter/": _telecommunity,
        "http://svn.eby-sarna.com/svnroot/": _telecommunity,
        "http://svn.eby-sarna.com/": _all,
        "gitlab.mister-muffin.de": _hostname_two_paths,  # requires login?
        "dev.gajim.org": _hostname_two_paths,
        "lab.louiz.org/poezio/": _hostname_two_paths,
        "hg.sr.ht/": _hostname_two_paths,
        "reine.cmla.ens-cachan.fr/c.truong/ruptures": _gitlab,
        "git.tiker.net/": _all,
        "git.lxch.eu/": _github,  # remove once https://github.com/pcdummy/vcs-mirrors/pull/1 is released
        "git.framasoft.org": partial(_gitlab, hostname="framagit.org"),
        "framagit.org": _gitlab,
        "git.videolan.org/?p=": _strip_after_dot_git,
        "git.sysmocom.de": _all,
        "git.linaro.org/": _linaro_org,
        "el-tramo.be/git/": _all,
        "jelmer.uk/code/": _hostname_two_paths,
        "workbench.dachary.org/dachary/": _hostname_two_paths,
        "http://git.p.engu.in/": _hostname_two_paths,
        "code.dealmeida.net": partial(
            _add_first_path, owner="robertodealmeida", hostname="bitbucket.org"
        ),
        "http://git.gnu.org.ua/cgit/": _strip_after_dot_git,
        "tracpub.yaco.es/djangoapps/wiki/OOT": _all,  # offline?
        "trac.tools.ietf.org/tools/": _hostname_two_paths,  # xml2rfc
        "spacepants.org/src/": _hostname_two_paths,  # uses arch for vcs
        "www.owlfish.com/software/": _hostname_two_paths,  # wsgiutils
        "owlfish.com/software/": _hostname_two_paths,
        "http://zesty.ca/python/": _hostname_two_paths,
        "http://code.krypto.org/": _all,
        "guaix.fis.ucm.es/projects/": _hostname_two_paths,
        "people.csail.mit.edu/hubert/": _hostname_two_paths,
        "owlfish.com/software/simpleTAL/": _hostname_two_paths,
        "www.panix.com/~asl2/software/": _hostname_three_paths,
        "www.bytereef.org/mpdecimal": _hostname_first_path,
        "www.theblobshop.com/pymock": _all,  # https://github.com/jmyounker excludes pymock
        "effbot.org/zone/element-tidylib.htm": _all,
        "http://www.alcyone.com/software/": partial(_hostname_two_paths, scheme="http"),
        "work.thaslwanter.at/thLib/html/": _all,
        "http://dalkescientific.com/Python/PyRSS2Gen.html": _all,
        "https://developer.nvidia.com/nvidia-management-library-nvml": _all,
        "http://www.excamera.com/sphinx/articles-openexr.html": _all,
        "wiki.mozilla.org/Auto-tools/Projects/Mozbase": _all,
        "wiki.mozilla.org/Auto-tools/Projects/Marionette": _all,
        "www.cosc.canterbury.ac.nz/~greg/python/Pyrex": _get_redirect_location,
        "www.csse.canterbury.ac.nz/greg.ewing/python/Pyrex/": _all,
        "http://www.aaronsw.com/2002/xmltramp": _hostname_two_paths,
        "www.hpl.hp.com/personal/Yasushi_Saito/pychart": _all,
        "web.archive.org/web/20170225171913/https://gna.org/projects/pychart": _all,
        "code.welldev.org": _all,
        "web.archive.org/web/20130829003029/http://code.larlet.fr/django-oauth/wiki/Home": _all,
        "svn.wiretooth.com/svn/open/pypicache": _all,
        "http://www.jsnp.net/code/": _all,
        "web.archive.org/web/2009*/http://svn.wiretooth.com/svn/open/pypicache/": _all,
        "web.archive.org/web/20131016122638/http://vehq.ru/project/django-extended-attachments/": _all,
        "hg.vehq.ru": _all,  # TODO: test entries on http://hg.vehq.ru/index.html
        "tracpub.yaco.es/djangoapps/wiki/": _all,
        "git.liw.fi/cgi-bin/cgit/cgit.cgi/": _all,  # ttystatus https://liw.fi/ttystatus/
        "www.funaba.org/code": _all,
    }

    def _get_fixer(self, url):
        for host, func in self.fixers.items():
            if _match_hostname(url, host, require_path=False):
                return func

    @autolog
    def get_root(self, url):
        return self._get_root(url)

    @cached(cache=LRUCache(maxsize=32))
    def _get_root(self, url):
        func = self._get_fixer(url)
        if func:
            rv = func(url)
            if not rv:
                return rv
            if isinstance(rv, tuple):
                if len(rv) == 3:
                    hostname, owner, repo = rv
                else:
                    owner, repo = rv
                    hostname = "github.com"
                if not owner or not repo:
                    return

                at = repo.find("@")
                if at != -1:
                    repo = repo[:at]

                if (
                    repo.endswith(".git")
                    or repo.endswith(".svg")
                    or repo.endswith(".png")
                ):
                    repo = repo[:-4]

                # https://github.com/lipoja/URLExtract/issues/13
                repo = repo.strip(".")  # ebcdic / CodecMapper description
                # github-team-organizer -> https://github.com/theskumar/python-dotenv)
                repo = repo.strip(")")

                if "bitbucket.org/" in url:
                    return "https://bitbucket.org/{}/{}".format(owner, repo)
                elif "/gitlab.com/" in url:
                    return "https://gitlab.com/{}/{}".format(owner, repo)
                else:
                    return "https://{}/{}/{}".format(hostname, owner, repo)

            if url.startswith("http://github.com"):
                url = "https://github.com" + url[len("http://github.com") :]
            elif "opendev.org" in url and url.endswith("/"):
                url = url[:-1]
            return rv
