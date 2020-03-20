from ._compat import urljoin


def get_html_hrefs(content, source_url, only_unique=False, ignore="github.io"):
    from lxml import html

    urls = []
    tree = html.fromstring(content.encode("utf-8"))
    for e in tree.xpath("//*[@href]"):
        link = e.attrib.get("href")
        if len(link) < 2:
            continue
        if link[0] == "/" or link[0] == ".":
            if not source_url:  # pragma: no cover
                continue
            if ignore and ignore in source_url:  # pragma: no cover
                continue
            link = urljoin(source_url, link)
        elif link[0] == "#":  # pragma: no cover
            continue
        elif link.startswith("javascript:"):  # pragma: no cover
            continue
        elif ignore and ignore in link:  # pragma: no cover
            continue

        if only_unique and link in urls:  # pragma: no cover
            continue

        link = urljoin(source_url, link)

        urls.append(link)

    return urls
