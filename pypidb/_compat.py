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

__all__ = ["PY2", "logger_helper", "urlparse", "urlsplit", "urljoin", "parse_qs"]
