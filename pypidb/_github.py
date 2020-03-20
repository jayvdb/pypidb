import base64
import json
import os

from appdirs import user_cache_dir
from logging_helper import setup_logging

from ._cache import get_file_cache_session
from ._similarity import normalize

gh_session = get_file_cache_session("gh")

logger = setup_logging()


def api_call(endpoint, method, field_name=None):
    endpoint = endpoint.lstrip("/")
    headers = {}
    cache_dir = user_cache_dir("gh")
    logger.info("Using cache directory: {}.".format(cache_dir))

    api_token = os.getenv("GITHUB_API_TOKEN")
    if api_token:  # pragma: no cover
        logger.info("Using API token")
        headers["Authorization"] = "token {}".format(api_token)

    gh_session.headers.update(headers)

    if method == "GET":
        r = gh_session.get(
            "https://api.github.com/{}".format(endpoint), headers=headers
        )
        try:
            rj = r.json()
        except json.JSONDecodeError:  # pragma: no cover
            logger.error("failed to decode {}:\n{}".format(endpoint, r.text))
            raise

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

        if r.status_code == 404:
            logger.warning("status code 404")


def check_repo(url_or_slug):
    if url_or_slug.startswith("https://github.com/"):
        slug = url_or_slug[len("https://github.com/") :]
    else:
        slug = url_or_slug

    r = api_call(endpoint="/repos/{}".format(slug), method="GET")
    if r.get("message", "") == "Not Found":
        return
    return r


def get_repo_setuppy(url_or_slug, normalised_name):
    if url_or_slug.startswith("https://github.com/"):  # pragma: no cover
        slug = url_or_slug[len("https://github.com/") :]
    else:
        slug = url_or_slug

    try:
        languages = api_call(endpoint="/repos/{}/languages".format(slug), method="GET")
    except (NameError, SystemExit) as e:  # pragma: no cover
        logger.warning("get_repo_setuppy gh {} failed {}".format(slug, e))
        return
    try:
        top_language = next(iter(languages))
    except StopIteration:
        return False
    logger.info("top lang = {}".format(top_language))
    if top_language != "Python":
        return False
    setuppy = None
    to_check = ["setup.py", "pyproject.toml", "setup.cfg"]
    if normalised_name in ["bobo", "infi-clickhouse-orm"]:
        to_check = ["buildout.cfg"]
    if normalised_name in ["pygam"]:
        to_check = ["flit.ini"]
    if normalised_name in ["spark-sklearn"]:
        to_check = ["build.sbt"]
    if normalised_name == "pyficache":
        to_check = ["__pkginfo__.py"]
    if normalised_name == "tensorboard":
        to_check = ["package.json"]
    if normalised_name in ["py9p", "juicer"]:
        to_check = ["setup.py.in"]
    if normalised_name in ["infi-execute"]:
        to_check = ["setup.in"]

    for filename in to_check:
        try:
            c = api_call(
                endpoint="/repos/{}/contents/{}".format(slug, filename),
                method="GET",
                field_name="content",
            )
        except Exception as e:  # pragma: no cover
            logger.warning("gh {} failed {}".format(slug, e))
            continue
        if not c:
            continue
        c = base64.b64decode(c).decode("utf-8")
        c = normalize(c)
        if not setuppy:
            setuppy = c
        if normalised_name in c:
            return c
        try:
            logger.info("{} not found in {}".format(normalised_name, c))
        except Exception:  # pragma: no cover
            logger.info("{} not found in {}".format(normalised_name, filename))

    logger.warning("{} not found in {}".format(normalised_name, to_check))
    return setuppy
