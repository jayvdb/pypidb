import urlextract

from ._html import get_html_hrefs

try:
    _url_extractor = urlextract.URLExtract(cache_dns=False)
except Exception:
    _url_extractor = urlextract.URLExtract()

MAX_URLS = 1000


def _url_extractor_base(content):
    try:
        return _url_extractor.gen_urls(content, check_dns=True)
    except Exception:
        return _url_extractor.gen_urls(content)


def _url_extractor_wrapper(content, url=None):
    extractor = _url_extractor_base(content)
    seen = set()
    for url in extractor:
        # package and cffi end up with repo``
        # https://github.com/lipoja/URLExtract/issues/13
        url = url.strip("`")

        if url.endswith(".html."):  # lit
            url = url[:-1]

        yield url

        seen.add(url)
        if len(seen) == MAX_URLS:
            return


def _url_extractor_wrapper_no_dns(content, url):
    return _url_extractor.find_urls(content, only_unique=True, check_dns=False)


def _url_no_extract(content, url):
    return []


def _url_extract_both(content, url):
    for url in get_html_hrefs(content, url):
        yield url
    for url in _url_extractor_wrapper(content, url):
        yield url
