from logging_helper import setup_logging

from ._cache import get_file_cache
from ._compat import urlsplit

_lp_client = None
logger = setup_logging()


def _get_lp():
    from lplight.client import LaunchpadClient
    import lplight.client

    web_session = get_file_cache("launchpad")
    lplight.client.requests = web_session

    global _lp_client

    if _lp_client is None:
        _lp_client = LaunchpadClient()
    return _lp_client


def _launchpad_bug(bug_id):
    lp_client = _get_lp()
    try:
        r = lp_client.get_bug_tasks(bug_id)
    except Exception as e:  # pragma: no cover
        logger.error("_launchpad_bug: {}".format(e))
        return

    if not r:  # pragma: no cover
        return
    data = r.json()
    project1 = data["entries"][0]["bug_target_name"]
    return _launchpad("https://launchpad.net/{}".format(project1))


def _launchpad(url):
    p = urlsplit(url)
    subdomain = p.netloc.split(".")[0]
    if subdomain == "launchpad":
        subdomain = None

    path = p.path[1:]
    if not path:  # pragma: no cover
        return
    name, _, other = path.partition("/")

    if not name:  # pragma: no cover
        return

    if name == "bugs":
        bug_id = other
        return _launchpad_bug(bug_id)
    elif name == "api":  # pragma: no cover
        path2, _, other = other.partition("/")
        path3, _, other = other.partition("/")
        name = path3
    elif name[0] == "~":
        if subdomain in ["bazaar", "code"]:
            path2, _, other = other.partition("/")
            path3, _, other = other.partition("/")
            name += "/" + path2 + "/" + path3
        else:
            return

    if not name:  # pragma: no cover
        raise RuntimeError("could not extract name from {}".format(url))

    lp_client = _get_lp()
    try:
        r = lp_client.get_project(name)
    except Exception as e:
        logger.error("_launchpad: {}".format(e))
        return
    if not r:
        return
    data = r.json()
    if not data.get("is_valid", True):  # pragma: no cover
        return

    check_url = data.get("homepage_url")
    logger.debug("lp homepage: {}".format(check_url))
    if not check_url:
        bzr_identity = data.get("bzr_identity")
        if bzr_identity and bzr_identity.startswith("lp:"):
            logger.debug("lp bzr id: {}".format(bzr_identity))
            return _launchpad("https://launchpad.net/{}".format(bzr_identity[3:]))

        check_url = data["web_link"]
        logger.debug("lp weblink: {}".format(check_url))

    if check_url != url:
        from ._scm_url_cleaner import SCMURLCleaner

        subcleaner = SCMURLCleaner()
        if "launchpad.net" not in check_url:
            logger.info("checking url {}".format(check_url))
            redirect = subcleaner.get_root(check_url)
            logger.info("checking url {} = ".format(redirect))
            if redirect:
                return redirect

    if "pypi.org" in url or "pypi.python.org" in url:
        return

    return "https://launchpad.net/{}".format(name)
