import base64
import json
import os

from appdirs import user_cache_dir
from logging_helper import setup_logging

from ._cache import get_file_cache_session
from ._similarity import normalize

gh_session = get_file_cache_session("gh")

logger = setup_logging()


class GitHubAPIMessage(Exception):
    pass


def api_call(endpoint, method, field_name=None):
    endpoint = endpoint.lstrip("/")
    headers = {}

    api_token = os.getenv("GITHUB_API_TOKEN")
    if api_token:  # pragma: no cover
        logger.info("Using API token")
        headers["Authorization"] = "token {}".format(api_token)

    gh_session.headers.update(headers)

    if method == "GET":
        r = gh_session.get(
            "https://api.github.com/{}".format(endpoint), headers=headers
        )

        logger.info("r status code {}: {}".format(r.status_code, r.reason))

        if r.status_code in [404]:
            raise GitHubAPIMessage("Not Found")

        r.raise_for_status()

        try:
            rj = r.json()
        except json.JSONDecodeError:  # pragma: no cover
            logger.error("failed to decode {}:\n{}".format(endpoint, r.text))
            raise

        if list(rj.keys()) == ["message", "documentation_url"]:
            raise GitHubAPIMessage(rj["message"])

        if field_name:
            if field_name in rj:
                return rj[field_name]
            else:
                logger.error("{} not in {}".format(field_name, rj.keys()))
        else:
            try:
                return r.json()
            except json.JSONDecodeError as e:  # pragma: no cover
                logger.error("failed to decode {}: {}\n{}".format(endpoint, e, r.text))
                raise


def check_repo(url_or_slug):
    if url_or_slug.startswith("https://github.com/"):
        slug = url_or_slug[len("https://github.com/") :]
    else:
        slug = url_or_slug

    try:
        r = api_call(endpoint="/repos/{}".format(slug), method="GET")
    except GitHubAPIMessage as e:
        if str(e) == "Not Found":
            return
        raise
    return r


def get_repo_top_language(slug):  # pragma: no cover
    try:
        languages = api_call(endpoint="/repos/{}/languages".format(slug), method="GET")
    except GitHubAPIMessage:
        raise
    except (NameError, SystemExit) as e:  # pragma: no cover
        logger.warning("get_repo_setuppy gh {} failed {}".format(slug, e))
        return
    try:
        return next(iter(languages))
    except StopIteration:
        return False
    logger.info("top lang = {}".format(top_language))


def repo_is_python(slug):  # pragma: no cover
    top_language = get_repo_top_language(slug)
    logger.info("{}: top lang = {}".format(slug, top_language))
    return top_language == "Python"


def api_get_file(slug, filename):  # pragma: no cover
    try:
        c = api_call(
            endpoint="/repos/{}/contents/{}".format(slug, filename),
            method="GET",
            field_name="content",
        )
    except GitHubAPIMessage as e:
        if str(e) == "Not Found":
            return
        else:
            raise
    except Exception as e:  # pragma: no cover
        logger.warning("gh {} failed {}".format(slug, e))
        raise
    if not c:
        return
    return base64.b64decode(c).decode("utf-8")


def raw_get_file(slug, filename):
    url = "https://raw.githubusercontent.com/{}/master/{}".format(slug, filename)
    r = gh_session.get(url)
    if r.status_code == 404:
        return
    r.raise_for_status()
    try:
        return r.content.decode(r.apparent_encoding)
    except Exception:
        return r.content.decode("utf-8")


def get_repo_setuppy(url_or_slug, matches, filenames=None):
    if url_or_slug.startswith("https://github.com/"):  # pragma: no cover
        slug = url_or_slug[len("https://github.com/") :]
    else:
        slug = url_or_slug

    if not isinstance(matches, list):
        matches = [matches]

    setuppy = None
    if not filenames:
        filenames = ["setup.py", "pyproject.toml", "setup.cfg"]

    for filename in filenames:
        try:
            c = raw_get_file(slug, filename)
        except Exception as e:
            logger.warning("gh raw {} {}: failed {}".format(slug, filename, e))
            continue
        if not c:
            continue
        c = normalize(c)
        if not setuppy:
            setuppy = c
        if all(match in c for match in matches):
            return c
        try:
            logger.info("{} not found in {}".format(matches, c))
        except Exception:  # pragma: no cover
            logger.info("{} not found in {}".format(matches, filename))

    logger.warning("{}: {} not found in {}".format(slug, matches, filenames))
    return setuppy
