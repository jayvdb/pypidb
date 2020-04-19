from __future__ import unicode_literals
import sys

try:
    from urllib.parse import urlparse, urlsplit, urljoin, parse_qs
except ImportError:  # pragma: no cover
    from urlparse import urlparse, urlsplit, urljoin, parse_qs

try:
    import logger_helper
except ImportError:  # pragma: no cover
    logger_helper = None

PY2 = sys.version_info[0] == 2

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
