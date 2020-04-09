import unittest

from r2c_isg.apis import api_map
from r2c_isg.loaders import Loader
from r2c_isg.loaders.web import webloader_map
from r2c_isg.structures import Dataset
from r2c_isg.structures.projects import PypiProject
from r2c_isg.structures.projects import project_map as registry_map
from tqdm import tqdm

from pypidb._compat import PY2
from tests.utils import _stdlib_all

if PY2:
    raise unittest.SkipTest("datasets not supported on Python 2")

R2C_WEB_CACHE = "tests/.datasets_requests_cache"


class PortingdbLoader(Loader):

    _pypi_name_mapping = {
        "django-database-url": "dj-database-url",
        "django-email-url": "dj-email-url",
        "django-search-url": "dj-search-url",
        "dns": "dnspython",
        "epi": "entry_point_inspector",
        "github3py": "github3.py",
        "glusterfs-api": "gfapi",
        # 'hwdata': 'pciutils', according to https://github.com/xsuchy/python-hwdata/blob/master/setup.py , but that is also not pypi name
        "jupyter-polymake": "jupyter-kernel-polymake",
        "libcloud": "apache-libcloud",
        "novaclient-os-networks": "os_networksv2_python_novaclient_ext",
        "novaclient-os-virtual-interfaces": "os_virtual_interfacesv2_python_novaclient_ext",
        "podman-api": "podman",
        "pycolumnize": "columnize",
        "pyhunspell": "hunspell",
        "pyobd": "obd",
        "pyosmium": "osmium",
        "pywt": "PyWavelets",
        "rtslib": "rtslib-fb",
        "sphinx-theme-alabaster": "alabaster",
        "sphinx-theme-py3doc-enhanced": "sphinx-py3doc-enhanced-theme",
        "uri-templates": "uritemplate",
        "webpy": "web.py",
        "XStatic-termjs": "XStatic-term.js",
        "zmq": "pyzmq",
    }

    _not_pypi = [
        "azure-sdk",
        "basemap-data",
        "blivet",
        "caja",
        "collectd_systemd",  # pypi_name is wrong
        "conda-package-handling",
        "configshell",
        "coverage-test-runner",
        "cpio",
        "distutils-extra",  # http://launchpad.net/python-distutils-extra/
        "docs",
        "evic",  # pypi_name is wrong
        "firkin",
        "gradunwarp",
        "gstreamer1",
        "gtkextra",
        "gzipstream",
        "hwdata",  # name should be 'pciutils' according to https://github.com/xsuchy/python-hwdata/blob/master/setup.py , but that is also not pypi name
        "iep",  # pypi URL wrong
        "ipgetter",  # ipgetter2 repo https://github.com/phoemur/ipgetter is missing
        "linux-procfs",  # http://userweb.kernel.org/python-linux-procfs (also mirrored on github)
        "lxc",
        "olpcgames",
        "phyghtmap",
        "pip-epel",
        "postgresql",
        "pyatspi",
        "pybox2d",  # box2d is different https://code.google.com/p/pybox2d
        "pycanberra",
        "pycxx",  # http://cxx.sourceforge.net/
        "pyev",  # setup.py checked; it is pyev
        "pyflowtools",
        "pygiftiio",
        "pygobject2",
        "pygobject3",
        "pygtk2",
        "pyhoca-cli",
        "pyhoca-gui",
        "pyoptical",
        "pyotherside",
        "pyrpmmd",
        "pysvn",
        "pythia8",
        "pyxtrlock",
        "pyzy",
        "rpmautospec",
        "rpm-generators",
        "schedutils",
        "simpleline",
        "smartcols",
        "socksipychain",
        "ttystatus",
        "typeshed",  # Removed from PyPI
        "uranium-lulzbot",  # uranium
        "vevents",
        "virtkey",  # https://launchpad.net/virtkey/
        "visionegg-quest",  # visionegg
        "x2go",
        "xapp",
    ]

    @staticmethod
    def get_pypi_name(package_name):
        if package_name.endswith("rpm-macros"):
            return

        if package_name.startswith("python-"):
            name = package_name[7:]
        elif package_name.startswith("python2-") or package_name.startswith("python3-"):
            name = package_name[8:]
        elif package_name.startswith("py"):
            name = package_name
        else:
            return

        # multiple packages, per version
        if name[-1].isdigit():
            if package_name in ["python26", "python27", "python3"]:
                return
            if package_name[:-1] == "python3":
                return
            if name.startswith("tornado"):
                return
            if name.startswith("pytest"):
                return
            if name.startswith("eric"):
                return
            if name.startswith("Django"):
                return
            if name.startswith("markdown"):
                return
            if name.startswith("prompt_toolkit"):
                return
            if name.startswith("wxpython"):
                return

        if name in PortingdbLoader._not_pypi:
            return

        if name in [
            "barbicanclient",
            "box",
            "can",
            "cinderclient",
            "congressclient",
            "daemon",
            "dateutil",
            "dbusmock",
            "debian",
            "debianbts",
            "designateclient",
            "editor",
            "engineio",
            "fedora",
            "gammu",
            "gilt",
            "glanceclient",
            "heatclient",
            "hglib",
            "hpilo",
            "iptables",
            "ironicclient",
            "k8sclient",
            "Levenshtein",
            "libdiscid",
            "ly",
            "lzo",
            "magic",
            "magnumclient",
            "manilaclient",
            "memcached",  # also python3-memcached
            "mistralclient",
            "mpd",
            "mpd2",
            "multilib",
            "mystrom",
            "networkmanager",
            "neutronclient",
            "novaclient",
            "nss",
            "octaviaclient",
            "opendata-transport",
            "openid",
            "openid-cla",
            "openid-teams",
            "pam",
            "poppler-qt4",
            "poppler-qt5",
            "qt5",
            "registry",
            "rsdclient",
            "saharaclient",
            "sane",
            "socketio",
            "stdnum",
            "string_utils",
            "swiftclient",
            "tackerclient",
            "uinput",
            "vitrageclient",
            "xmp-toolkit",
            "zaqarclient",
        ]:
            return "python-" + name

        if name in [
            "acoustid",
            "alsa",
            "alsaaudio",
            "collada",
            "cpuinfo",
            "enchant",
            "hamcrest",
            "smbc",
            "smi",
            "svg",
            "winrm",
        ]:
            return "py" + name

        if name in ["nose-xcover", "paste-script", "paste-deploy"]:
            return name.replace("-", "")

        if name in ["btchip", "edgegrid", "mmtf"]:
            return name + "-python"

        return PortingdbLoader._pypi_name_mapping.get(name, name)

    @classmethod
    def weblists(cls) -> dict:
        return {
            "fedora": {
                "getter": PortingdbLoader._get_fedora,
                "parser": PortingdbLoader._parse_fedora,
            }
        }

    @classmethod
    def load(cls, name: str, **kwargs) -> Dataset:
        # get the request type (weblist vs. organization)
        from_type = kwargs.pop("from_type")
        if from_type in ["user", "org"]:
            raise Exception(
                "portingdb does not support loading project lists from user/org names."
            )

        # initialize a registry
        ds = Dataset(**kwargs)

        # select the correct weblist loader/parser
        weblists = cls.weblists()
        if name not in weblists:
            raise Exception(
                "Unrecognized portingdb weblist name. Valid "
                "options are: %s" % list(weblists)
            )

        # load the data
        data = weblists[name]["getter"](api=ds.api, **kwargs)

        # parse the data
        weblists[name]["parser"](ds, data)

        return ds

    @staticmethod
    def _get_fedora(api, **kwargs) -> list:
        url = "https://raw.githubusercontent.com/fedora-python/portingdb/master/data/fedora.json"

        status, data = api.request(url, **kwargs)
        if status != 200:
            raise Exception("Error downloading %s; is the url accessible?", url)

        for name, record in data.items():
            record["project"] = PortingdbLoader.get_pypi_name(name)

        # python- is only ~2000 of ~3800
        return [record for name, record in data.items() if record["project"]]

    @staticmethod
    def _parse_fedora(ds: Dataset, data: list) -> None:
        # map data keys to project keywords
        uuids = {"name": lambda p: p.project}

        # create the projects
        ds.projects = [
            PypiProject(uuids_=uuids, **d)
            for d in tqdm(data, desc="         Loading", unit="project", leave=False)
        ]


class OpenSUSEOBSLoader(Loader):

    _pypi_name_mapping = {
        "abseil": "absl-py",
        "antlr3_runtime": "antlr3-python-runtime",
        "dialog": "python2-pythondialog",
        "fastTSNE": "openTSNE",
        "pocketsphinx-python": "pocketsphinx",
    }

    _not_pypi = [
        "aci-integration-module",  # https://github.com/noironetworks/aci-integration-module
        "atomicwrites-doc",
        "avocado-plugins-vt",
        "babel-doc",
        "distutils-extra",  # http://launchpad.net/python-distutils-extra/
        "dukpy-kovidgoyal",  # https://github.com/kovidgoyal/dukpy ; conflicts with dukpy
        "epubmerge",  # https://github.com/JimmXinu/EpubMerge/issues/5
        "espeak",  # https://launchpad.net/python-espeak
        "espressomd",
        "espressopp",  # https://github.com/espressopp/espressopp/issues/66
        "goocanvas",  # https://github.com/GNOME/pygoocanvas
        "gtksourceview",
        "jaraco.base",
        "jedihttp",  # https://github.com/vheon/JediHTTP/issues/17
        "kasa",
        "killswitch",  # http://blog.homac.de
        "liblarch",  # https://live.gnome.org/liblarch
        "linux-procfs",  # http://userweb.kernel.org/python-linux-procfs (also mirrored on github)
        "nose-random",  # https://github.com/xlwings/nose-random/issues/2
        "oci-sdk",
        "onionshare",  # https://github.com/micahflee/onionshare/issues/910 (packaging related)
        "pycxx",  # http://cxx.sourceforge.net/
        "pygments-style-railscasts",  # https://github.com/DrMegahertz/pygments-style-railscasts is 404
        #                               https://github.com/JoeyButler/pygments-style-railscasts might be ok
        "pyGRID",  # that name is now PySyft, but https://github.com/dedalusj/pyGRID is unrelated
        "pyotherside",  # http://thp.io/2011/pyotherside/
        "pysvn",  # http://pysvn.tigris.org/
        "sge-pygame",  # http://stellarengine.nongnu.org
        "testtools-doc",
        "typeshed",  # package deleted from PyPI
        "virtkey",  # https://launchpad.net/virtkey/
        "xcaplib",  # https://github.com/AGProjects/python-xcaplib
        "zope.proxy-doc",
    ]

    @staticmethod
    def get_pypi_name(package_name):
        if package_name.endswith("rpm-macros"):
            return

        if package_name.startswith("python-"):
            name = package_name[7:]
        elif package_name.startswith("python2-") or package_name.startswith("python3-"):
            name = package_name[8:]
        else:
            return

        # multiple packages, per version
        if name[-1].isdigit():
            if name.startswith("tornado"):
                return
            if name.startswith("pytest"):
                return
            if name.startswith("eric"):
                return
            if name.startswith("Django"):
                return
            if name.startswith("prompt_toolkit"):
                return
            if name.startswith("wxpython"):
                return

        if name.lower() in OpenSUSEOBSLoader._not_pypi:
            return

        if name.startswith("xsge-") or name.startswith("xsge_"):
            return

        if name == "azure-sdk":
            return  # meta package

        if name.lower() in [
            "3parclient",
            "axolotl",
            "axolotl-curve25519",
            "debian",
            "djvulibre",
            "iptables",
            "keyczar",
            "levenshtein",
            "markdown-math",
            "mhash",
            "nss",
            "sane",
            "yamldoc",
        ]:
            return "python-" + name

        if name.lower() in [
            "cairo",
            "cddb",
            "gpgme",
            "gtk",
            "opengl",
            "opengl-accelerate",
            "parted",
            "usb",
        ]:
            return "py" + name

        if name.lower() in OpenSUSEOBSLoader._not_pypi:
            return

        return OpenSUSEOBSLoader._pypi_name_mapping.get(name, name)

    @classmethod
    def weblists(cls) -> dict:
        return {
            "devel:languages:python": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:pytest": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:numeric": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:django": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:flask": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:jupyter": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:avocado": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:mailman": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:certbot": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:azure": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:aws": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
            "devel:languages:python:misc": {
                "getter": OpenSUSEOBSLoader._get_project,
                "parser": OpenSUSEOBSLoader._parse_project,
            },
        }

    @classmethod
    def load(cls, name: str, **kwargs) -> Dataset:
        # get the request type (weblist vs. organization)
        from_type = kwargs.pop("from_type")
        if from_type in ["user", "org"]:
            raise Exception(
                "opensuse OBS does not support loading project lists from user/org names."
            )

        # initialize a registry
        ds = Dataset(**kwargs)

        # select the correct weblist loader/parser
        weblists = cls.weblists()
        if name not in weblists:
            raise Exception(
                "Unrecognized opensuse OBS weblist name. Valid "
                "options are: %s" % list(weblists)
            )

        # load the data
        data = weblists[name]["getter"](api=ds.api, project=name, **kwargs)

        # parse the data
        weblists[name]["parser"](ds, data)

        return ds

    @staticmethod
    def _get_project(api, project, **kwargs) -> list:
        url = "https://build.opensuse.org/package?length=2000&project="
        url += project

        status, data = api.request(url, **kwargs)
        if status != 200:
            raise Exception("Error downloading %s; is the url accessible?", url)

        data = data["data"]

        for record in data:
            name = record["name"]
            start_pos = name.find(">") + 1
            end_pos = name.find("<", start_pos)
            name = name[start_pos:end_pos]
            record["project"] = OpenSUSEOBSLoader.get_pypi_name(name)

        return [record for record in data if record["project"]]

    @staticmethod
    def _parse_project(ds: Dataset, data: list) -> None:
        # map data keys to project keywords
        uuids = {"name": lambda p: p.project}

        # create the projects
        ds.projects = [
            PypiProject(uuids_=uuids, **d)
            for d in tqdm(data, desc="         Loading", unit="project", leave=False)
        ]


webloader_map["portingdb"] = PortingdbLoader
registry_map["portingdb"] = registry_map["pypi"]
api_map["portingdb"] = api_map["pypi"]

webloader_map["opensuse"] = OpenSUSEOBSLoader
registry_map["opensuse"] = registry_map["pypi"]
api_map["opensuse"] = api_map["pypi"]


def get_top_packages(kind="top4kmonth"):
    ds = Dataset.load_web(
        name=kind,
        from_type="list",
        registry="pypi",
        cache_dir=R2C_WEB_CACHE,
    )

    for project in ds.projects:
        yield project.get_name()


def get_fedora_packages():
    ds = Dataset.load_web(
        name="fedora",
        from_type="list",
        registry="portingdb",
        cache_dir=R2C_WEB_CACHE,
    )

    names = set([project.get_name() for project in ds.projects])
    return names


def get_opensuse_packages(project):
    ds = Dataset.load_web(
        name=project,
        from_type="list",
        registry="opensuse",
        cache_dir=R2C_WEB_CACHE,
    )

    # Avoid dups like python2-cmd2 and python-cmd2
    names = set([project.get_name() for project in ds.projects])
    return names


def _intersect_stdlib(kind="top4kyear"):
    for name in get_top_packages(kind):
        if name not in _stdlib_all:
            continue
        yield name
