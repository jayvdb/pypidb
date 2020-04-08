import io

import unidiff
from logging_helper import setup_logging

from ._url_extract import _url_extractor_wrapper

logger = setup_logging()


def _get_raw_patch_url(url):
    assert url.startswith("https://github.com/") or url.endswith(".patch"), url
    if "/pull/" in url:
        slug = url[len("https://github.com/") : url.find("/pull/")]
        pull_id = url.rsplit("/", 1)[1]
        url = "https://patch-diff.githubusercontent.com/raw/{}/pull/{}.patch".format(
            slug, pull_id
        )
    else:
        assert url.endswith(".patch"), url

    return url


def _get_patch_redirects(patch, allow_add_only=False):
    f = io.StringIO(patch.decode("utf-8"))
    p = unidiff.PatchSet(f)
    redirect_mappings = []

    for p_file in p:
        for p_hunk in p_file:
            removed_urls = []
            added_urls = []
            for p_line in p_hunk:
                if p_line.line_type == "-":
                    removed_urls += _url_extractor_wrapper(str(p_line))
                    logger.debug("removed_urls: {}".format(removed_urls))
                elif p_line.line_type == "+":
                    added_urls += _url_extractor_wrapper(str(p_line))
                    logger.debug("added_urls: {}".format(added_urls))

            for url in added_urls.copy():
                if url in removed_urls:
                    removed_urls.remove(url)
                    added_urls.remove(url)
                elif not url.startswith("http://") and not url.startswith("https://"):
                    added_urls.remove(url)

            if not allow_add_only:
                if removed_urls:
                    assert added_urls
                elif added_urls:
                    assert removed_urls

            if not removed_urls and not allow_add_only:
                logger.info("Skipping url patch {} {}".format(removed_urls, added_urls))
                continue

            if len(set(added_urls)) == 1:
                to_url = added_urls[0]
                if allow_add_only and not removed_urls:
                    removed_urls.append(None)

                for url in removed_urls:
                    redirect_mappings.append((url, to_url))
            elif not added_urls:
                for url in removed_urls:
                    redirect_mappings.append((url, None))
            else:
                if len(added_urls) != len(removed_urls):
                    logger.info(
                        "Hunk ignored as removed cant be mapped to added: {}\n{}".format(
                            removed_urls, added_urls
                        )
                    )
                    continue
                for i, to_url in enumerate(added_urls):
                    redirect_mappings.append((removed_urls[i], to_url))

    return redirect_mappings
