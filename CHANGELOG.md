Changelog
=========

0.2.4 (2020-04-10)
------------------
PyPI package rules added/updated:

* `awshelpers`: Prevent wrong result
* `azureml-mlflow`: Fix result
* `azure*`: Ignore dev.azure.com URLS to improve performance
* `bert-serving-client`: Allow same repository as `bert-serving-server`
* `calendar`: Add email rule to accept webpage
* `certifi`: Remove unnecessary rule due to upstream fixes
* `comet-ml`: Prevent wrong result
* `config`: Add email rule to find Bitbucket repository
* `dai-sgqlc-3-5`: Prevent matching sgqlc
* `darcsver`: Prevent matching Babel
* `databricks-connect`: Prevent wrong result
* `dateutils`: Add patch
* `dbus-python`: Add email rule to find gitlab.freedesktop.org repository
* `dbus-signature-pyparsing`: Add patch
* `detect-delimiter`: Add SCM git.nzoss.org.nz
* `kivy-deps-`: Prevent wrong result
* `galaxy*`: Increase http timeouts to allow correct result, and flag monorepo
* `geoip`: Add email rule to find old MaxMind repository
* `hs-dbus-signature`: Add patch
* `libevdev`: find gitlab.freedesktop.org repository
* `libvirt-python`: Add hack to reject libvirt C library repository
* `logging`: Add email rule to find Bitbucket repository
* `logreduce`: Update due to hoster softwarefactory-project.io changes
* `magic`: Ignore missing files
* `mulpyplexer`: Add email rule
* `plaidml`: Add email rule as fallback to ensure consistent result
* `plaidml-keras`: Allow same repository as `plaidml`
* `pyastronomy`: Increase fetch count to find repository
* `pymf`: Ignore missing files
* `python-graph-dot`: Allow same repository as `python-graph`
* `python-registry`: Add patch
* `py-trello`: Add patch
* `pyuwsgi`: Allow same respository as `uwsgi`
* `pyxdg`: Replace GitHub mirror with gitlab.freedesktop.org repository
* `requests-opentracing`: Fix match
* `robinhood-aiokafka`: Prevent matching aiokafka
* `ruffus`: Add patch
* `subgrab`: Add patch
* `tableauhyperapi`: Prevent matching `tableauserverclient`
* `tvb-gdist`: Remove patch merged upstream
* `unicode`: Block https to allow resolution
* `xpyb`: Ignore missing files

Fixes:
* adapters: Fix blocking of HTTP IPs
* SCM finder: Process URLs without any path (`/`)

Enhancements:
* rules: Implement url extraction maximum
* adapters: Create CDNBlockAdapter
* park_providers: Add allaboutcookies.org
* SCM finder: Handle issuetracker.google.com
* SCM finder: Remove trailing ) in repository names
* SCM picker: Improve freedesktop SCM
* SCM finder: Block github.com/notifications

Other:
* SCM finder: Add links to three URLExtract issues
* tests/datasets: Map Fedora packages registry and magic to PyPI names
* tests/datasets: Add rpmautospec to `_not_pypi`
* tests/datasets: Remove grabserial from `_not_pypi`
* test_rtd: Update URL for simplekml
* tests/data: Update URL for graphql-core
* test_top: Test top packages for last 30 days
* tests: Move gnome tests into test_frameworks.py class
* test_fedora: Mark tilestache as failure
* tests: Ignore tensorboard-plugin-wit failure

0.2.3 (2020-03-29)
------------------
PyPI package rules added/updated:

* `amazon-dax-client`: Prevent incorrect result, as no result is known
* `archinfo`: Add patch to find correct repository
* `azure*`: Fix many packages to return correct result instead of docs repo
* `bpython`: Add missing result
* `flup`: Add required trailing slash to URL
* `getchanges`: Remove unnecessary patch to find correct repo
* `maxminddb`: Fix result
* `msgpack-python`: Limit to one http fetch to improve speed
* `openstacksdk`: Use opendev.org instead of OpenStack storyboard
* `pigpio`: Add email rule to fallback to correct result
* `pyfim`: No result
* `pygal`: Workaround website failure
* `pygame`: Add email rule due to website failure
* `pyke`: Ignore no files in PyPI
* `pymilia`: Ignore no files in PyPI
* `pystatgrab`: Ignore no files in PyPI
* `pyrex`: Follow redirect to current webpage
* `pytest-codestyle`: Map to pytest-pycodestyle
* `should-dsl`: Add patch to workaround broken
* `tvb-gdist`: Add patch to improve performance
* `ujson*`: Prevent mapping to incorrect or stale forks

Fixes:
- GitHub: Fix rule processing bug with tuples
- GitHub: Consistently raise exception on API limit exceeded

Enhancements:
- Implement basic cli
- Cache: Add HTTPS exclusions and blockages to improve performance
- Cache: Reduce max redirects to 10.
- Link extraction: Rewrite /#!/foo to /foo
- Link extraction: Detect self-hosted readthedocs websites
- SCM picker: Use pyup.io links to find SCM
- SCM picker: Remove unnecessary openstack storyboard resolver
- Patch: Allow remove only patches.
- GitHub: Use raw to fetch files for verification, reducing API usage

Other:
- Moved package name verification filenames into rules
- Expand CI, rerunning failures and skipping API limit failures
- Increase coverage to 90%
- Improve CI verification of xstatic-*, Fedora and openSUSE packages
- Fix test verification of several packages
- `https-everything-py` was released, removing need to install `master`

0.2.2 (2020-03-20)
------------------
Fixes:
- Add park_providers.txt to sdist

Other
- Add Cirrus CI testing TestTop360, excluding 'jupyter'.


0.2.1 (2020-03-20)
------------------
- Initial upload.
