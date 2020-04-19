from __future__ import unicode_literals
import sys

from urllib3.util.url import parse_url as urlparse

try:
    from urllib.parse import urljoin, parse_qs
except ImportError:  # pragma: no cover
    from urlparse import urljoin, parse_qs

try:
    import logger_helper
except ImportError:  # pragma: no cover
    logger_helper = None

PY2 = sys.version_info[0] == 2

urlsplit = urlparse

if PY2:
    StringTypes = (str, "".__class__)
else:
    StringTypes = (str, )

__all__ = [
    "PY2",
    "StringTypes",
    "logger_helper",
    "parse_qs",
    "urljoin",
    "urlparse",
    "urlsplit",
]
