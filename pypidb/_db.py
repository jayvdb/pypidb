from logging_helper import setup_logging

from ._similarity import normalize

logger = setup_logging()

mappings = {
    "tornado-proxy": "https://github.com/senko/tornado-proxy",
    "pbr": "https://opendev.org/openstack/pbr",
    "flux": "https://github.com/vmalloc/flux",
    "readthedocs-org": "https://github.com/rtfd/readthedocs.org",
}

reverse_mappings = {
    "https://opendev.org/openstack/project-config": "project-config",  # doesnt exist
    "https://github.com/hypothesisworks/hypothesis-python": "hypothesis",  # old url
    "https://github.com/logentries/lecli": "logentries-lecli",
    "https://github.com/senko/tornado-proxy": "tornado-proxy",
    "https://bitbucket.org/ubernostrum/django-contact-form": "django-contact-form",
    "https://gitlab.com/nekokatt/hikari.core": "hikari",
    "https://github.com/rtfd/readthedocs.org": "readthedocs.org",
    "https://sourceforge.net/projects/pywin32": "pywin32",
    "https://github.com/snide/sphinx_rtd_theme": "sphinx-rtd-theme",
    "https://opendev.org/openstack-dev/pbr": "pbr",
    "https://github.com/vmalloc/flux": "flux",
    "https://github.com/getslash/flux": "flux",
    "https://github.com/esnme/ultrajson": "ujson",
}

multipackage_repos = {
    "https://github.com/antlr/antlr3",
    "https://github.com/googleapis/googleapis",
    "https://wiki.mozilla.org/Auto-tools/Projects/Mozbase",
    "https://github.com/h2oai/sparkling-water",
    "https://github.com/manahl/pytest-plugins",
    "https://github.com/census-instrumentation/opencensus-python",
    "https://github.com/pyca/cryptography",
    "https://github.com/aws/aws-cli",
    "https://sourceforge.net/projects/turbogears1",
    "https://code.google.com/p/tgtools",
    "https://github.com/pedersen/tgtools",
    "https://code.google.com/p/ibm-db",
    "https://github.com/ibmdb/python-ibmdb",
    "https://github.com/googleapis/google-cloud-python",
    "https://github.com/marrow/mailer",
    "https://gitlab.gnome.org/GNOME/pygobject",
    "https://github.com/buildout/buildout",
    "https://www.riverbankcomputing.com/software/sip",
    "https://www.riverbankcomputing.com/software/pyqt",
    "https://www.bytereef.org/mpdecimal",
    "https://github.com/gfxmonk/termstyle",
    "https://github.com/OpenMined/PySyft",
    "https://github.com/plaidml/plaidml",
    "https://github.com/Kami/python-yubico-client",
    "https://sourceforge.net/projects/pyopengl",
    "https://github.com/mcfletch/pyopengl",
    "https://github.com/henry0312/pytest-codestyle",  # rename
    "https://github.com/Azure/azure-cli",
    "https://github.com/Microsoft/vsts-python-api",
    "https://github.com/Azure/azure-sdk-for-python",
    "https://github.com/Azure/azure-cosmosdb-python",
    "https://github.com/Azure/azure-kusto-python",
    "https://github.com/Azure/azure-storage-python",
    "https://github.com/fabioz/PyDev.Debugger",
    "https://github.com/galaxyproject/galaxy",
    "https://github.com/kyamagu/faiss-wheels",
    "https://github.com/unbit/uwsgi",
    "https://github.com/pmatiello/python-graph",
    "https://github.com/hanxiao/bert-as-service",
}
multipackage_repos = set(i.lower() for i in multipackage_repos)

_fetch_mapping = {}


def add_mapping(name, url):
    assert url is not None
    assert url != "http://sourceforge.net/p/turbogears1/code/"
    logger.info("Adding mapping {} = {}".format(name, url))
    normalised_name = normalize(name)
    mappings[normalised_name] = url
    if url.lower() not in multipackage_repos:
        # lower needed for hacking pycqa = PyCQA
        reverse_mappings[url.lower()] = (normalised_name, name)


def add_failed_mapping(name, err):  # pragma: no cover
    assert isinstance(err, Exception)
    logger.info("Adding failed mapping {} = {}".format(name, err))
    normalised_name = normalize(name)
    mappings[normalised_name] = err


def db_clear():  # pragma: no cover
    mappings.clear()
    reverse_mappings.clear()


class Database(object):
    def __init__(self, **kwargs):
        from ._pypi import Converter

        self._converter = Converter(**kwargs)
        self.website_timeout = self._converter.website_timeout
        self.projects = {}

    def find_project_scm_url(self, name):
        normalized_name = normalize(name)
        url = self._converter.get_vcs(normalized_name)
        self.projects[normalized_name] = url
        return url

    get_vcs = find_project_scm_url
