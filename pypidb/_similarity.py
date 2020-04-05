import collections
import logging
import re

import textdistance
from logging_helper import setup_logging

from pypidb._compat import PY2, logger_helper, urlsplit

logger = setup_logging()
if logger_helper and not PY2:
    autolog = logger_helper.LoggerHelper(logging.getLogger(__name__), logging.DEBUG)
else:  # pragma: no cover
    autolog = lambda x: x

_similarity_func = textdistance.RatcliffObershelp().distance


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


@autolog
def _compute_similarity(name, url, algo=_similarity_func, comp_op=min):
    name = normalize(name).replace("-", "")

    p = urlsplit(url)
    path = p.path
    path = path[1:]
    first, _, second = path.rstrip("/").rpartition("/")
    first = first.replace("/", ".")
    first = normalize(first).replace("-", "")
    second = normalize(second).replace("-", "")

    if second:
        if second.endswith(".git"):  # pragma: no cover
            second = second[:-4]
    elif first.endswith(".git"):  # pragma: no cover
        first = first[:-4]

    if first.startswith("?p="):  # pragma: no cover
        first = first[3:]

    logger.debug("_similarity of {} {} to {}".format(first, second, name))

    last = second if second else first

    results = [
        algo(name, second),
        algo(name, first + second),
        algo(name, second + first),
        algo("py" + name, second),
        algo("py" + name, first + second),
        algo(name + "py", second),
        algo(name + "py", first + second),
        algo(name + "python", second),
        algo(name + "python", first + second),
        algo(name, last + "python"),
        algo(name, "python" + last),
        algo(name, last.replace("python", "").replace("--", "-").strip("-")),
        algo(
            name,
            last.replace("python", "").replace("sdk", "").replace("--", "-").strip("-"),
        ),
        algo(name, last.replace("sdk", "").replace("--", "-").strip("-")),
        algo(name, last + "py"),
        algo(name, "py" + last),
        algo(name, "backports-" + last),
        algo("python" + name + "client", last),  # yubico
        algo("python" + name, last + "client"),
        algo(name + "client", last),
        algo(name + "python-client", last),
        algo(name + "client-python", last),
        algo(name, last + "python-client"),
        algo(name, last + "client"),
        algo(name, last + "client-python"),
        0.1 + algo(name, last + "-ctypes"),  # yara
        algo(
            "backports-" + name, last + "ffi"
        ),  # https://github.com/r3m0t/backports.lzma
        0.1 + algo(name, "django-" + last),  # django-vz-wiki
        0.1 + algo("django-" + name, last),
        0.1 + algo(name.replace("django", "drf"), last),  # django-extra-fields
        0.1 + algo(name.replace("drf", "django"), last),
        algo(name.replace("drf", "django-rest-framework"), last),  # drf-jwt
        algo(name, last.replace("drf", "django-rest-framework")),
    ]

    return comp_op(results)


@autolog
def _get_weighted_best(name, urls, cond):
    name_cleaned = name.lower().replace("_", "").replace("-", "")

    counter = collections.Counter(url for url in urls if cond(name_cleaned, url))

    if not counter:
        return

    logger.debug("counter - {}".format(counter))

    most_common = counter.most_common()

    if len(most_common) == 1:  # pragma: no cover
        return most_common[0][0]

    # ignore items of same weight
    if most_common[0][1] == most_common[1][1]:
        return [i[0] for i in most_common if i[1] == most_common[0][1]]

    return most_common[0][0]


@autolog
def _get_most_similar(name, urls):
    data = dict((url, _compute_similarity(name, url)) for url in set(urls))
    logger.debug("computed similarity: {}".format(data))

    nearest_value = None
    nearest_counter = collections.Counter()
    nearest_url = None
    for url, value in data.items():
        nearest_counter[value] += 1
        if nearest_value is None or value < nearest_value:
            logger.debug("nearest: {} {}".format(value, url))
            nearest_value = value
            nearest_url = url
    logger.debug("nearest_counter {}".format(nearest_counter))
    if nearest_counter[nearest_value] != 1:
        # Identical similarity for different values
        logger.debug(
            "identical similarity {} times: {}".format(
                nearest_counter[nearest_value], nearest_value
            )
        )
        return

    return nearest_url


def clean_url(url):
    return url.lower().replace("_", "").replace("-", "").rstrip("/")


def _slash_endswith(name_cleaned, url):
    return clean_url(url).endswith("/" + name_cleaned)


def _endswith(name_cleaned, url):
    return clean_url(url).endswith(name_cleaned)


def _python_and_name_match(name_cleaned, url):
    url = clean_url(url)
    return "python" in url and name_cleaned in url


def _only_name_match(name_cleaned, url):
    return name_cleaned in clean_url(url)


@autolog
def _get_shortest(urls):
    shortest = min(len(url) for url in urls)
    urls = [url for url in urls if len(url) == shortest]
    if len(urls) > 1:
        return

    return urls[0]


@autolog
def _get_prefered(urls):
    orig_urls = urls

    freedesktop_urls = [url for url in urls if "gitlab.freedesktop.org" in url]
    if len(freedesktop_urls) == 1:
        return freedesktop_urls[0]

    freedesktop_urls = [url for url in urls if "cgit.freedesktop.org" in url]
    if len(freedesktop_urls) == 1:
        return freedesktop_urls[0]

    opendev_urls = [url for url in urls if "opendev.org" in url]
    if len(opendev_urls) == 1:
        return opendev_urls[0]

    urls = [url for url in urls if "code.google.com" not in url]
    if len(urls) == 1:
        return urls[0]
    elif not urls:  # pragma: no cover
        urls = orig_urls

    urls = [url for url in urls if "sourceforge.net" not in url]
    if len(urls) == 1:
        return urls[0]
    elif not urls:  # pragma: no cover
        urls = orig_urls

    shortest = _get_shortest(urls)
    if shortest:
        logger.debug("using shortest")
        return shortest

    logger.debug("using urls[0]")
    return urls[0]


@autolog
def get_best_match(name, urls):
    accepted = urls

    best = _get_weighted_best(name, accepted, _slash_endswith)

    if best:
        if isinstance(best, str):
            return best
        accepted = best

    best = _get_weighted_best(name, accepted, _endswith)

    if best:
        if isinstance(best, str):
            return best
        accepted = best

    best = _get_weighted_best(name, accepted, _python_and_name_match)

    if best:
        if isinstance(best, str):
            return best
        accepted = best

    best = _get_weighted_best(name, accepted, _only_name_match)

    if best:
        if isinstance(best, str):
            return best
        accepted = best

    most_common = _get_weighted_best(name, accepted, lambda x, y: True)

    logger.debug("!!!!finding similar: {}".format(accepted))
    most_similar = _get_most_similar(name, set(accepted))

    # Reject multiple
    if not isinstance(most_common, str):
        accepted = most_common
        most_common = None

    if not most_common and not most_similar:
        return _get_prefered(accepted)

    logger.debug("common, similar: {} - {}".format(most_common, most_similar))
    if most_common == most_similar:
        logger.debug("most common and most similar: {}".format(most_common))
        return most_common
    elif most_common:
        logger.debug("most common: {}".format(most_common))
        return most_common
    elif most_similar:
        logger.debug("most similar w/ identical commonality: {}".format(most_similar))
        return most_similar
    else:  # pragma: no cover
        return _get_prefered(accepted)
