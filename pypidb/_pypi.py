import json
import re

import requests
from fake_useragent import UserAgent
from logging_helper import setup_logging
from requests.exceptions import TooManyRedirects
from socialregexes import identify
from socialregexes.socialregexes import definitions as social_definitions
from stdlib_list import stdlib_list

from ._cache import _check_url_domain, get_file_cache_session, get_timeout
from ._db import _fetch_mapping, add_mapping, db_clear, mappings
from ._exceptions import (
    IncompletePackageMetadata,
    InvalidPackage,
    InvalidPackageVersion,
    PackageWithoutFiles,
    PackageWithoutUrls,
    UnrecognisedStdlibBackport,
)
from ._github import normalize
from ._rtd import get_repo as get_rtd_repo
from ._rules import DefaultRule, _find_named_repo, rules
from ._scm_url_cleaner import SCMURLCleaner
from ._similarity import _compute_similarity, get_best_match
from ._stdlib import ALLOWED_STDLIB_BACKPORTS
from ._types import Email, Name, Text, Url, UrlSet, Webpage

try:
    import brotli
except ImportError:
    brotli = None


logger = setup_logging()

_stdlib_all = stdlib_list()

social_definitions.update(
    {
        "gitlab": re.compile(r"https?://(?:www\.)?gitlab.com/([a-zA-Z0-9-]+)$"),
        "identica": re.compile(r"https?://(?:www\.)?identi.ca/([a-zA-Z0-9-]+)$"),
        "delicious": re.compile(r"https?://(?:www\.)?delicious.com/([a-zA-Z0-9-]+)$"),
        "delicious-api-1": re.compile(
            r"https?://api.del.icio.us/v1/js/[a-z]*/([a-zA-Z0-9-]+)?"
        ),
        "delicious-api-2": re.compile(
            r"https?://api.del.icio.us/v2/json/([a-zA-Z0-9-]+)/"
        ),
        "flattr": re.compile(r"https?://(?:www\.)?flattr.com/@([a-zA-Z0-9-]+)$"),
        "google": re.compile(
            r"^https?://profiles\.google\.com/((?:\+[a-zA-Z0-9.]+)|[0-9]+)$"
        ),
        "gravatar": re.compile(r"https?://www.gravatar.com/avatar.php?gravatar_id="),
    }
)

_DEFAULT_HEADERS = {
    "User-Agent": UserAgent().google,
    "Accept": "text/html,text/plain,application/*;q=0.8,text/*;q=0.5",
    "Accept-Encoding": "br,gzip;q=0.9,deflate;q=0.8"
    if brotli
    else "gzip,deflate;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}


class Converter(object):
    def __init__(
        self,
        session=None,
        repo_url="https://pypi.org/pypi",
        website_timeout=13,
        max_fetches=None,
        clear_db=False,
        store_fetch_list=False,
    ):
        self.session = session
        self.web_session = session
        self._cleaner = SCMURLCleaner()
        self.repo_url = repo_url
        self.website_timeout = website_timeout
        self._max_fetch_count = max_fetches
        self.max_distance = 0.2
        self._store_fetch_list = store_fetch_list
        self.headers = _DEFAULT_HEADERS
        if clear_db:
            db_clear()

    def _get(self, *path):
        if self.session is None:
            self.session = get_file_cache_session("json")
        try:
            return self.session.get(
                self.repo_url.rstrip("/") + "/" + "/".join(path),
                allow_redirects=True,
                headers=self.headers,
            )
        except TooManyRedirects:
            # Simply repeat https://github.com/ionrock/cachecontrol/issues/214
            return requests.get(
                self.repo_url.rstrip("/") + "/" + "/".join(path),
                allow_redirects=True,
                headers=self.headers,
            )

    def _get_package_json(self, name):
        response = self._get("{0}/json".format(name))
        if response.status_code == 404:
            raise InvalidPackage("Invalid package name {}".format(name))
        else:
            data = json.loads(response.text)
            if not data:
                raise InvalidPackage("Invalid package data for name {}".format(name))
            return data

    def _accept_url(self, rule, name, url):
        url = self._cleaner.get_root(url)
        if not url:
            return url

        rv = rule.reject_match(name, url)
        if isinstance(rv, str):
            return rv
        elif rv:
            return False

        return url

    def _group_urls(self, urls, name):
        matches = set()
        related = set()
        non_matches = set()
        for url in urls:
            if name in url:
                matches.add(url)
            elif "python" in url.lower():
                related.add(url)
            elif "download" in url.lower():
                related.add(url)
            else:
                non_matches.add(url)
        return list(matches) + list(related) + list(non_matches)

    def _exclude_non_urls(self, urls):
        return set(
            url
            for url in urls
            if not url.endswith(".gz")
            and not url.endswith(".tgz")
            and not url.endswith(".xz")
            and not url.endswith(".bz2")
            and not url.endswith(".zip")
            and not url.endswith(".jar")
            and not url.endswith(".rar")
            and not url.endswith(".exe")
            and url != "UNKNOWN"
            and "ntp.org" not in url  # ntplib code excerpt
        )

    def _normalise_urls(self, urls):
        new_urls = set()
        for url in urls:
            hash_pos = url.find("#")
            if hash_pos == -1:
                new_urls.add(url)
            elif url[hash_pos - 1:].startswith("/#!/"):
                # http://travis-ci.org/#!/ misspellings, yara
                new_urls.add(url.replace("/#!/", "/"))
            else:
                new_urls.add(url[:hash_pos])
        return new_urls

    def _check_metadata(self, data):
        project_info = data["info"]
        name = project_info["name"]
        email = project_info.get("author_email", project_info.get("maintainer_email"))
        if not email:
            raise IncompletePackageMetadata(
                "{} has no email in PyPI metadata".format(name)
            )
        if (
            email != "UNKNOWN"
            and "@" not in email
            and " at " not in email
            and "_at_" not in email
        ):
            raise InvalidPackage(
                '{} has invalid email "{}" in PyPI metadata'.format(name, email)
            )

        license = project_info.get("license")
        if not license:
            raise IncompletePackageMetadata(
                "{} has no license in PyPI metadata".format(name)
            )

        summary = project_info.get("summary")
        if not summary:
            raise IncompletePackageMetadata(
                "{} has no summary in PyPI metadata".format(name)
            )

    def _check_artifacts(self, data):
        name = data["info"]["name"]
        check = data.get("releases")
        if not check:
            raise PackageWithoutFiles(
                "{} has no releases in PyPI metadata".format(name)
            )

        version = data["info"].get("version")
        if not version:
            raise InvalidPackageVersion(
                "{} has no version in PyPI metadata".format(name)
            )
        if version == "0" or set(version) == {"0", "."}:
            raise InvalidPackageVersion(
                "{} has version {} in PyPI metadata".format(name, version)
            )

        check = data.get("urls")
        if not check:
            raise PackageWithoutFiles(
                "{} (version {}) has no files in PyPI metadata".format(name, version)
            )

    def _get_inputs(self, rule, name, data):
        project_info = data.get("info", {})
        if not project_info:
            raise PackageWithoutFiles("{} has no info in PyPI metadata".format(name))
        name = project_info.get("name")
        if not name:
            raise InvalidPackage('{} has no "name" in PyPI metadata'.format(name))

        inputs = []

        project_urls = urls = project_info.get("project_urls") or []
        if urls:
            urls = list(urls.values())

        for key, value in project_info.items():
            if key.endswith("_url") and value and value != "UNKNOWN":
                if value not in project_urls:
                    urls.append(value)

        if not project_urls:
            self._check_artifacts(data)

            normalised_name = normalize(name)
            if normalised_name in _stdlib_all and name not in ALLOWED_STDLIB_BACKPORTS:
                raise UnrecognisedStdlibBackport(
                    "Package name {} conflicts with stdlib and is not a known backport".format(
                        name
                    )
                )

        if urls:
            urls_pre_dns = self._exclude_non_urls(urls)
            urls = set(url for url in urls_pre_dns if _check_url_domain(url))
            if urls_pre_dns != urls:
                logger.info(
                    "urls with domains not resolving: {}".format(
                        set(urls_pre_dns) - urls
                    )
                )

        emails = self._split_emails(project_info)
        summary = project_info.get("summary", "")
        description = project_info.get("description", "")

        redirects = rule.url_redirects()
        if redirects:
            for from_, to_ in redirects:
                if from_ and from_ in urls:
                    urls.remove(from_)
                    if to_:
                        urls.add(to_)
                elif to_:
                    urls.add(to_)

        if urls:
            inputs.append(UrlSet(urls))

        if summary:
            inputs.append(Text(summary, "summary"))

        if description:
            inputs.append(Text(description, "description"))

        for email in emails:
            inputs.append(Email(email))

        if not emails:
            inputs.append(Name(name))

        return inputs

    def _get_vcs_links(self, rule, name, data, inputs):
        normalized_name = normalize(name)
        results = []
        previous_results = None
        max_fetch_count = max(rule.fetch_count, self._max_fetch_count or 0)
        fetch_list = []
        seen_list = []
        fetch_count = 0
        queue = inputs[:]

        logger.debug("queue {}".format(queue))

        while queue:
            must_accept = False
            item = queue.pop(0)
            try:
                logger.debug(
                    "processing {}: {}".format(
                        item.__class__.__name__, item.source or item
                    )
                )
            except UnicodeEncodeError:
                logger.debug(
                    "processing {} (item decode problem)".format(
                        item.__class__.__name__
                    )
                )

            result_url = None
            if isinstance(item, UrlSet):
                urls = item.value
                urls = self._exclude_non_urls(urls)
                urls = self._normalise_urls(urls)

                if not urls:
                    continue

                seen_list += list(urls)

                fetch_urls = []
                result_urls = []

                for url in urls:
                    rv = self._accept_url(rule, name, url)
                    if rv:
                        results.append(rv)
                        result_urls.append(rv)
                    elif rv is not False:
                        fetch_urls.append(url)

                if len(result_urls) == 1 and len(fetch_list) <= 1:
                    results.append(result_urls[0])

                if result_urls:
                    logger.debug(
                        "--results from {}: {}".format(item.value, result_urls)
                    )
                else:
                    logger.debug("--none of this set: {}".format(item.value))

                logger.debug("queuing {}".format(sorted(fetch_urls)))
                for url in self._group_urls(fetch_urls, name):
                    queue.append(Url(url))

                logger.info(
                    "{}: from {} added urls {}".format(
                        name, item.source, sorted(result_urls)
                    )
                )

            elif isinstance(item, Text):
                if fetch_count > max_fetch_count:
                    logger.info("Not processing text from {}".format(item.source))
                    continue

                text = item.value
                if not text:
                    continue
                try:
                    urls = set(rule.link_extract(text, item.source))
                except Exception:
                    urls = []
                logger.debug(
                    "@@ ran {} on text size {} for {} urls !!".format(
                        rule.link_extract, len(text), len(urls)
                    )
                )
                logger.debug("extracted {}".format(sorted(urls)))
                queue.append(UrlSet(urls, item.source))

            elif isinstance(item, Email):
                email = item.value
                result_url = _find_named_repo(name, [email])
                must_accept = True

            elif isinstance(item, Name):
                item_name = item.value
                result_url = _find_named_repo(item_name)
                must_accept = True

            elif isinstance(item, Url):
                url = item.value

                if url in fetch_list:
                    logger.debug("queue loop skipping already fetched {}".format(url))
                    continue

                if url.startswith("https://github.com") or url.startswith(
                    "http://github.com"
                ):  # see github rule below
                    if ".github.com" not in url:
                        logger.debug("queue loop skipping github {}".format(url))
                        continue

                if fetch_count > max_fetch_count:
                    logger.debug(
                        "queue loop skipping >{}: {}".format(max_fetch_count, url)
                    )
                    continue

                user = identify(url)
                if user:
                    logger.info("{} detected as social for {}".format(url, user))
                    continue

                rv = rule.reject_url(name, url.lower())
                logger.debug("reject rule {}: {}".format(url, rv))
                if rv in ["", None]:
                    continue
                if rv is True:
                    continue

                if (
                    "github.com" in url and ".github.com" not in url
                ):  # yara, pykalman, membrete, zvmcloudconnector
                    logger.debug("queue loop skipping github v2 {}".format(url))
                    continue

                if self.web_session is None:
                    self.web_session = get_file_cache_session("web")

                if url.startswith("git://"):  # TODO: create tidy phase
                    url = url[6:]

                if not url.startswith("http://") and not url.startswith("https://"):
                    if "/" not in url:
                        url = "http://" + url + "/"
                    elif "://" not in url:
                        url = "http://" + url
                try:
                    logger.info("r {}".format(url))
                    r = self.web_session.get(
                        url, headers=self.headers, timeout=get_timeout(url)
                    )
                    logger.debug(
                        "r {}.url {} elapsed {}".format(
                            r.__class__.__name__, r.url, r.elapsed
                        )
                    )
                    logger.debug("r {} headers: {}".format(r.url, r.headers))
                    r.raise_for_status()
                except Exception as e:
                    logger.warning("{}: {}".format(url, e))
                    continue

                urls = []
                if r.url != url:
                    urls.append(r.url)

                if r.headers.get("X-RTD-Project"):
                    rtd_url = get_rtd_repo(r.headers.get("X-RTD-Project"))
                    if rtd_url:
                        logger.warning("{}: rtd {}".format(url, rtd_url))
                        urls.append(rtd_url)

                if urls:
                    queue.append(UrlSet(set(urls)))

                if not r.text:
                    logger.warning("{}: empty page".format(url))
                else:
                    queue.append(Webpage(r, url))
                    fetch_list.append(url)
                    fetch_count += 1

            if not result_url and results and results != previous_results:
                result_url = get_best_match(rule.match, results)
                previous_results = results[:]

            if result_url:
                score = _compute_similarity(rule.match, result_url)
                if must_accept or score < self.max_distance:
                    if self._store_fetch_list:
                        _fetch_mapping[normalized_name] = fetch_list

                    return result_url

            if not queue and not results:
                ph_url = "https://pythonhosted.org/{}/".format(name)
                if ph_url not in seen_list:
                    queue.append(Url(ph_url))

        logger.debug("fetched {}".format(fetch_list))
        if self._store_fetch_list:
            _fetch_mapping[normalized_name] = fetch_list

        if results:
            return get_best_match(rule.match, results)

    def _split_emails(self, project_info):
        emails = set(
            [project_info.get("author_email"), project_info.get("maintainer_email")]
        )
        emails = [
            email
            for email in emails
            if email and not email.startswith("UNKNOWN") and "@" in email
        ]
        logger.debug("emails {}".format(emails))
        split_emails = []
        for emails in emails:
            parts = emails.split(",")
            split_emails += [i.strip() for i in parts if i.strip() and "@" in i]
        return set(split_emails)

    def _add_mappings(self, names):
        for name in names:
            logger.debug("---- preloading {} ----".format(name))
            url = self.get_vcs(name)
            assert url
            add_mapping(name, url)
            logger.debug("---- preloaded {} = {} ----".format(name, url))

    def get_vcs(self, name):
        normalised_name = normalize(name)
        logger.info("looking up {}".format(name))
        cached_result = mappings.get(normalised_name)
        if cached_result:
            if isinstance(cached_result, str):
                return cached_result
            raise cached_result

        data = self._get_package_json(name)
        project_info = data.get("info", {})
        if not project_info:
            logger.debug(data)
            raise PackageWithoutFiles("{} has no info in PyPI metadata".format(name))

        name = project_info.get("name")
        if not name:
            raise InvalidPackage('{} has no "name" in PyPI metadata'.format(name))

        rule = rules.get(normalised_name)
        if not rule:
            rule = DefaultRule(name)
        logger.debug("rule {} {}".format(rule.__class__.__name__, rule))
        if rule.preload:
            self._add_mappings(rule.preload)

        inputs = self._get_inputs(rule, name, data)

        try:
            url = self._get_vcs_links(rule, name, data, inputs)
        except PackageWithoutUrls as err:
            logger.error(
                "_get_vcs_links({}) raised PackageWithoutUrls {!r}".format(name, err)
            )
            raise

        logger.debug("_get_vcs_links({}) returned .. {}".format(name, url))
        if not url:
            self._raise_no_result_exception(rule, name, data)

        if (
            normalised_name in _stdlib_all
            and normalised_name not in ALLOWED_STDLIB_BACKPORTS
        ):
            raise UnrecognisedStdlibBackport(
                "Package name {} ({}) conflicts with stdlib and is not a known backport".format(
                    name, url
                )
            )

        logger.debug("{}: found {}".format(name, url))

        if not rule.ignore_bad_metadata:
            self._check_artifacts(data)

        check_url = self._cleaner.get_root(url)
        assert check_url == url, "get_root({}) => {}".format(url, check_url)

        add_mapping(name, url)
        return url

    def _raise_no_result_exception(self, rule, name, data):
        project_info = data.get("info", {})
        if not project_info:
            raise PackageWithoutFiles("{} has no info in PyPI metadata".format(name))
        name = project_info.get("name")
        if not name:
            raise InvalidPackage('{} has no "name" in PyPI metadata'.format(name))

        self._check_artifacts(data)
        self._check_metadata(data)

        project_urls = urls = project_info.get("project_urls")
        urls = set(urls.values()) if urls else set()
        emails = self._split_emails(project_info)
        summary = project_info.get("summary", "")
        description = project_info.get("description", "")

        if not description:
            logger.info("summary and description missing from {}".format(project_info))
            raise IncompletePackageMetadata(
                "{} has no description in PyPI metadata".format(name)
            )

        raise PackageWithoutUrls("{} has no usable urls in PyPI metadata".format(name))
