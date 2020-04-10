#!/usr/bin/env python
"""PyPI client side database."""

"""
Copyright 2020 John Vandenberg

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import find_packages, setup

__version__ = "0.2.4"

classifiers = """\
Environment :: Console
Environment :: Web Environment
Intended Audience :: Developers
Intended Audience :: Science/Research
Intended Audience :: System Administrators
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: Implementation :: CPython
Development Status :: 3 - Alpha
"""

setup(
    name="pypidb",
    version=__version__,
    description="Local database of PyPI metadata to find VCS URLs",
    license="Apache-2.0",
    author_email="jayvdb@gmail.com",
    url="https://github.com/jayvdb/pypidb",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"": ["*.txt"]},
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*",
    install_requires=[
        "https-everywhere",
        "requests[security]",
        "brotlipy",  # urllib3 optional dep
        "CacheControl",
        "cachetools",
        "lockfile",
        "dns-cache",
        "diskcache",
        "fake-useragent",
        "appdirs",
        "click",
        "lxml",
        "lplight",
        "socialregexes",
        "stdlib-list",
        "urlextract",
        "textdistance",
        "unidiff",
        "logging-helper",
    ],
    classifiers=classifiers.splitlines(),
    entry_points='''
        [console_scripts]
        pypidb=pypidb.cli:cli
    ''',
    tests_require=["pytest-blockage", "unittest-expander"],
)
