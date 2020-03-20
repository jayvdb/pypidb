from ._cache import get_file_cache
from ._compat import urlsplit

web_session = get_file_cache("web")


def _pagure_io(url):
    p = urlsplit(url)
    path = p.path[1:]
    path1, _, other = path.partition("/")
    path2, _, other = other.partition("/")

    if path2:
        r = web_session.get("https://pagure.io/api/0/{}/{}".format(path1, path2))
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "fullname" in data:
                return "https://pagure.io/{}/{}".format(path1, path2)

    r = web_session.get("https://pagure.io/api/0/{}".format(path1))
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, dict) and "fullname" in data:
            return "https://pagure.io/{}".format(path1)

    return
