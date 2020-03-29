Changelog
=========

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
