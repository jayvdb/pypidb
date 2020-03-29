# pypidb
PyPI client side database with SCM/VCS URLs

This project provides a client side database of [PyPI project metadata](https://pypi.org/),
primarily for the purpose of finding a SCM URL for any PyPI project.
More of the internals of the database will be exposed.  Time has been the
main limiting factor in exposing more.

Most programming languages created in the last 10 years directly connect
every library to a SCM.  PyPI offers several mechanisms for package uploads
to provide URLS, including for the SCM, however this is frequently omitted,
is often invalid, and is frequently outdated as projects move their development
activities between free hosting services, especially when services are
discontinued.  There are also projects which have deleted the project
on a hosted service and not republished it at a new location.
(Perhaps due to "right to vanish" provisions.)

This project attempts to locate the current development URL, and has
deep analysis in the test suite to verify the resolution process is
correct for thousands of projects.

Each resolution process stops after a limited number of web fetches,
and almost all projects tested require less than one minute per project,
and disk caching is used so that subsequent resolution of the same projects
are almost instantaneous.

The objective is to always give an appropriate URL for any project,
if there is one, and if there is a credible rationale that the project
in question is, or was, an important project.

If you encounter a project which returns the wrong result, or no result,
first check the PyPI metadata for a suitable SCM link.  If none exists,
try to find the development project manually, and create an issue in
their project to enhance the metadata they submit to PyPI.

Only if the target project maintainers are uncooperative, then create
an issue in the pypidb project for assistance.

## Details

There are over 8000 tests, however a few projects appear in multiple tests,
so the total number of projects checked is slightly lower.

Tests currently cover all PyPI projects in
* [`4,000 most-downloaded packages`](https://github.com/hugovk/top-pypi-packages)
* [`Fedora portingdb`](https://github.com/fedora-python/portingdb)
* [`openSUSE devel:languages:python*`](https://build.opensuse.org/project)

Of those, approximately 340 projects do not return a URL, such as
[`mysql-connector-python`](https://pypistats.org/packages/mysql-connector-python)
with over 55,000 downloads per day.

There are a few situations where the returned result may not be stable; where it
may alternate between two URLs.  The fluctuation is due to how URLs are
queued and fetched.  There are no known cases where this happens, however
override rules have been added to avoid them.
It is a high priority for any such occurrences to be fixed so that results are
always stable.   Please raise an issue if you encounter this.

There are many rules which drive the resolution, and each package can have
an associated [unified patch](https://pypi.org/project/unidiff/) URL,
which will be fetched and used to guide the resolution.
This is used for packages which have moved, but have not yet been re-released
to PyPI with updated metadata.

The rules for projects may also exclude URLs in the metadata from the resolution
process.
The rules do not allow for explicitly setting the target URL.
For projects which do not have a SCM, and only have a webpage, that webpage
can be added as a 'fake' SCM so that it will be used, however this approach
is only to be used for moribund projects where no SCM can be found.

## Usage

```
$ pip install pypidb
$ pypidb requests-threads
https://github.com/requests/requests-threads
$ pypidb does-not-exist
Invalid package name does-not-exist
```

```py
>>> from pypidb import Database

>>> db = Database()
>>> db.find_project_scm_url("requests-threads")
'https://github.com/requests/requests-threads'
>>> db.find_project_scm_url("mercurial")
'https://www.mercurial-scm.org/repo/hg'
>>> db.find_project_scm_url("cffi")
'https://foss.heptapod.net/pypy/cffi'
>>> db.find_project_scm_url("mysql-connector-python")
Traceback (most recent call last):
    ...
pypidb._exceptions.IncompletePackageMetadata: mysql-connector-python has no email in PyPI metadata
https://pypi.org/project/mysql-connector-python/8.0.19/: 500 Server Error: HTTPS Everywhere for url: https://pypi.org/project/mysql-connector-python/8.0.19/
https://pypi.org/project/mysql-connector-python/: 500 Server Error: HTTPS Everywhere for url: https://pypi.org/project/mysql-connector-python/
https://downloads.mysql.com/docs/licenses/connector-python-8.0-com-en.pdf: 500 Server Error: HTTPS Everywhere for url: https://downloads.mysql.com/docs/licenses/connector-python-8.0-com-en.pdf
https://downloads.mysql.com/docs/licenses/connector-python-8.0-gpl-en.pdf: 500 Server Error: HTTPS Everywhere for url: https://downloads.mysql.com/docs/licenses/connector-python-8.0-gpl-en.pdf
https://downloads.mysql.com/docs/licenses/connector-python-gpl-en.pdf: 500 Server Error: HTTPS Everywhere for url: https://downloads.mysql.com/docs/licenses/connector-python-gpl-en.pdf
https://downloads.mysql.com/docs/connector-python-en.pdf: 500 Server Error: HTTPS Everywhere for url: https://downloads.mysql.com/docs/connector-python-en.pdf
https://downloads.mysql.com/docs/licenses/connector-python-com-en.pdf: 500 Server Error: HTTPS Everywhere for url: https://downloads.mysql.com/docs/licenses/connector-python-com-en.pdf
```

Resolution of many packages uses Read the Docs metadata, which performs
better when using a token which can be obtained from
https://readthedocs.org/accounts/tokens/

It should be stored in the default [`.netrc`](https://docs.python.org/3/library/netrc.html)
file, in the user home, and should have the following format.

```
machine readthedocs.io
    login deadbeef
    password x-oauth-basic
```

To a lesser extent, the GitHub API is also used.  Depending on the volume of lookups,
it may be necessary to add a GitHub token, also stored in `.netrc`.

## Testing

Testing requires a GitHub token in `.netrc`.
Without a GitHub token, many tests will be skipped, and some will
fail.
(The tests can be easily fixed to detect that the API limit was reached)

```sh
git clone https://github.com/jayvdb/pypidb
cd pypidb
tox
```
A complete test run takes several hours.  There is aggressive caching
of web content using `CacheControl` and DNS results using `dns-cache`,
so subsequent runs should complete in a little over an hour.

Running only tests on the top 360 most popular PyPI packages can be done
without any tokens, and completes within approximately five minutes.
```sh
tox -- -k TestTop360
```
Similarly, running the tests on the top 4000 most popular PyPI packages can
be done without any tokens, and completes within approximately twenty minutes,
and tests requiring a GitHub token will be skipped.
```sh
tox -- tests/test_top.py
```

As the tests are inspecting and validating the results for live project
metadata, and those projects are constantly on the move, and the resolution
often includes accessing websites which may be inoperative temporarily for
various reasons (usually certificate expiration!), it is not unusual for
tests to fail.

For example there are approximately 700 expected URLS in `tests/data.py`,
divided into four subsets.  In the case of projects that have moved, and
the algorithm has correctly followed the move, those URLs need to be
updated.

There is rudimentary support for marking PyPI projects as untestable.
