import requests
from logging_helper import setup_logging
from requests.packages.urllib3.util.timeout import Timeout
from requests.utils import _parse_content_type_header

from https_everywhere.adapter import BlockAdapter, RedirectAdapter, _generate_response
from pypidb._compat import urlsplit

logger = setup_logging()


def get_file_lines(filename):
    with open(filename) as f:
        return set(i.lower() for i in f.read().splitlines() if not i[0] == "#")


class Status500Adapter(BlockAdapter):

    send = BlockAdapter.send_block


class IPBlockAdapter(BlockAdapter, RedirectAdapter):
    def send(self, request, *args, **kwargs):
        url = request.url
        if url.startswith("http"):
            if url[4] == "s":
                start = 8
            else:
                start = 7
            is_num = url[start].isdigit()
            is_IP = False
            logger.debug("is_num = {}; is_IP = {}: {}".format(is_num, is_IP, url))
            if is_num:
                ip_parts = url[start:].split(".", 3)
                logger.debug("ip_parts = {}: {}".format(ip_parts, url))
                if len(ip_parts) == 4:
                    ip_parts[3] = ip_parts[3].split("/", 1)[0]
                    logger.debug("ip_parts = {}: {}".format(ip_parts, url))
                    is_IP = all(part.isdigit() for part in ip_parts)
                elif ip_parts[0].startswith("localhost"):
                    is_IP = True
            logger.debug("is_IP = {}: {}".format(is_IP, url))
            if is_IP:
                return self.send_block(request, *args, **kwargs)

        logger.debug("IPblock of {} skipped".format(request.url))
        try:
            resp = super(IPBlockAdapter, self).send(request, *args, **kwargs)
        except Exception as e:
            resp = self.handle_error(e)
        return resp


class CDNBlockAdapter(BlockAdapter):
    cdn_prefixes = {
        "ajax",
        "assets",
        "cdn",
        "cdnjs",
        "fonts",
        "i",
        "img",
        "images",
        "imgix",
        "maxcdn",
        "media",
        "netdna",
        "static",
        "unpkg",  # unpkg.com
    }
    cdn_domains = {
        "a.trellocdn.com",
        "code.jquery.com",
    }

    def send(self, request, *args, **kwargs):
        url = request.url
        p = urlsplit(url)
        netloc = p.netloc.lower()
        parts = netloc.split(".")
        if parts[0] in self.cdn_prefixes or netloc in self.cdn_domains:
            return self.send_block(request, *args, **kwargs)

        logger.debug("cdn block of {} skipped".format(request.url))
        try:
            resp = super(CDNBlockAdapter, self).send(request, *args, **kwargs)
        except Exception as e:
            resp = self.handle_error(e)
        return resp


class DomainListBlockAdapter(BlockAdapter):
    def __init__(self, *args, **kwargs):
        blocklist = kwargs.pop("blocklist", None)
        super(DomainListBlockAdapter, self).__init__(*args, **kwargs)
        self._blocklist = None
        if blocklist:
            self._blocklist = get_file_lines(blocklist)

    def send(self, request, *args, **kwargs):
        url = request.url
        p = urlsplit(url)
        netloc = p.netloc.lower()
        for pattern in self._blocklist:
            if pattern in netloc:
                return self.send_block(request, *args, **kwargs)

        logger.debug("domain block of {} skipped".format(request.url))
        try:
            resp = super(DomainListBlockAdapter, self).send(request, *args, **kwargs)
        except Exception as e:
            resp = self.handle_error(e)
        return resp


class LoginBlockAdapter(BlockAdapter):

    _login_redirect_patterns = ["login", "signin"]
    _login_site_prefix = [
        "https://accounts.google.com/servicelogin",
        "https://open.login.yahooapis.com/openid/op/auth",
        "https://citeseer.ist.psu.edu/myciteseer/login",
        "http://login.developer.nvidia.com/",  # nvidia-ml-py
        "https://login.newrelic.com/login",  # newrelic
    ]

    def block_redirect(self, from_url, to_url):
        from_url_lower = from_url.lower()
        to_url_lower = to_url.lower()

        for pattern in self._login_redirect_patterns:
            if pattern not in from_url_lower and pattern in to_url_lower:
                return 403

    def send(self, request, *args, **kwargs):
        url_lower = request.url.lower()
        for prefix in self._login_site_prefix:
            if url_lower.startswith(prefix):
                return self.send_block(request, code=403, *args, **kwargs)

        try:
            resp = super(LoginBlockAdapter, self).send(request, *args, **kwargs)
        except Exception as e:
            resp = self.handle_error(e)

        if resp.status_code == 302:
            is_login_redirect = self.block_redirect(request.url, resp.url)

            if is_login_redirect:
                logger.info("blocking redirect to {}".format(resp.url))
                if "location" in resp:
                    del resp.headers["location"]
                resp.status_code = 403

        return resp


class ContentTypeBlockAdapter(BlockAdapter):
    def send(self, request, *args, **kwargs):
        try:
            resp = super(ContentTypeBlockAdapter, self).send(request, *args, **kwargs)
        except Exception as e:
            resp = self.handle_error(e)

        location = resp.headers.get("location")
        if location:
            return resp

        content_type = resp.headers.get("content-type")
        if not content_type:
            return self.send_block(request, code=500, *args, **kwargs)

        content_type, params = _parse_content_type_header(content_type)

        if content_type == "text/plain":
            try:
                resp.text
            except Exception as e:
                logger.error("text/plain which isnt plain text: {}".format(e))
                return self.send_block(request, code=406, *args, **kwargs)

        parts = content_type.split("/")
        if parts[0] not in ["text", "application"]:
            return self.send_block(request, code=406, *args, **kwargs)

        if parts[1] in ["json"]:
            return resp

        if parts[1] in ["javascript", "css"]:
            return self.send_block(request, code=406, *args, **kwargs)

        if parts[0] == "application":
            if "html" not in parts[1] and "xml" not in parts[1]:
                return self.send_block(request, code=406, *args, **kwargs)

        return resp


class HTTPSAdapter(RedirectAdapter):

    _head_timeout = Timeout(connect=10, read=5)

    def __init__(self, *args, **kwargs):
        https_exceptions = kwargs.pop("https_exceptions", [])
        super(HTTPSAdapter, self).__init__(*args, **kwargs)
        self._https_exceptions = https_exceptions

    def ignore_handle_error(self, exc, request=None):
        if not request:
            raise exc

        if request.url.startswith("https"):
            tail = request.url[8:]
            if self.prevent_https(tail):
                logger.info("downgrading to http", request.url, exc)
                new_request = request.copy()
                new_request.url = "http://" + tail
                return self.send(request, timeout=self._head_timeout)

        raise exc

    def block_redirect(self, from_url, to_url):
        pass

    def prevent_https(self, tail):
        if tail[0].isdigit():  # TODO: detect IP
            return True
        for rule in self._https_exceptions:
            if tail.startswith(rule):
                return True
        return False

    def send(self, request, *args, **kwargs):
        if request.url.startswith("https://"):
            tail = request.url[8:]
            if self.prevent_https(tail):
                logger.info("downgraded {} to http".format(request.url))
                request.url = "http://" + tail

        try:
            resp = super(HTTPSAdapter, self).send(request, *args, **kwargs)
        except Exception as e:
            resp = self.handle_error(e, request)
        return resp

    def get_redirect(self, url):
        if not url.startswith("http://"):
            return super(HTTPSAdapter, self).get_redirect(url)

        tail = url[7:]
        if self.prevent_https(tail):
            logger.info("https blocked for {}".format(url))
            return super(HTTPSAdapter, self).get_redirect(url)

        while True:
            current_url = url
            try:
                if current_url.startswith("http://code.google.com"):
                    resp = requests.get(
                        current_url, allow_redirects=False, timeout=self._head_timeout
                    )
                else:
                    resp = requests.head(
                        current_url, allow_redirects=False, timeout=self._head_timeout
                    )
                resp.raise_for_status()
            except Exception as e:
                logger.info("head failed for {}: {!r}".format(current_url, e))
                break
            else:
                logger.debug(
                    "head {} {} {} {} {}".format(
                        current_url, resp.url, resp, resp.headers, resp.content
                    )
                )
                location = resp.headers.get("location")
                if location and location != current_url:
                    code = self.block_redirect(current_url, location)
                    if code is True:
                        return super(HTTPSAdapter, self).get_redirect(url)
                    elif code:
                        return _generate_response(code)

                    code = self.block_redirect(url, location)
                    if code is True:
                        return super(HTTPSAdapter, self).get_redirect(url)
                    elif code:
                        return _generate_response(code)

                    if location.startswith("https:"):
                        tail = location[8:]
                        if self.prevent_https(tail):
                            return super(HTTPSAdapter, self).get_redirect(url)
                        return resp
                    url = location

                break

        tail = url[7:]
        if self.prevent_https(tail):
            logger.info("https blocked for {}".format(url))
            return super(HTTPSAdapter, self).get_redirect(url)
        return "https" + url[4:]
