from tests.utils import _TestBase


class TestNonSCM(_TestBase):
    def test_thLib(self):
        url = self.converter.get_vcs("thLib")
        self.assertInsensitiveEqual(url, "http://work.thaslwanter.at/thlib/html/")

    def test_PyRSS2Gen(self):
        url = self.converter.get_vcs("PyRSS2Gen")
        self.assertInsensitiveEqual(
            url, "http://dalkescientific.com/Python/PyRSS2Gen.html"
        )

    def _test_PyChart(self):
        url = self.converter.get_vcs("PyChart")
        self.assertInsensitiveEqual(
            url, "http://www.hpl.hp.com/personal/yasushi_saito/pychart"
        )
        # Also https://web.archive.org/web/20170225171913/https://gna.org/projects/pychart

    def test_SimpleTAL(self):
        url = self.converter.get_vcs("SimpleTAL")
        self.assertInsensitiveEqual(url, "https://owlfish.com/software/simpleTAL")

    def test_aaronsw_xmltramp(self):
        url = self.converter.get_vcs("xmltramp")
        self.assertInsensitiveEqual(url, "https://www.aaronsw.com/2002/xmltramp")


class TestPyPiMisc(_TestBase):
    def test_basic(self):
        url = self.converter.get_vcs("six")
        self.assertInsensitiveEqual(url, "https://github.com/benjaminp/six")

    def test_repoze_sphinx_autointerface(self):
        url = self.converter.get_vcs("repoze.sphinx.autointerface")
        self.assertInsensitiveEqual(
            url, "https://github.com/repoze/repoze.sphinx.autointerface"
        )

    def test_repoze_sphinx_autointerface_hyphen(self):
        url = self.converter.get_vcs("repoze-sphinx-autointerface")
        self.assertInsensitiveEqual(
            url, "https://github.com/repoze/repoze.sphinx.autointerface"
        )

    def test_py_ext(self):
        url = self.converter.get_vcs("scp")
        self.assertInsensitiveEqual(url, "https://github.com/jbardin/scp.py")

    def test_aexpect(self):
        url = self.converter.get_vcs("aexpect")
        self.assertInsensitiveEqual(url, "https://github.com/avocado-framework/aexpect")

    def test_pythondialog(self):
        url = self.converter.get_vcs("pythondialog")
        self.assertInsensitiveEqual(
            url, "https://sourceforge.net/projects/pythondialog"
        )

    def test_wsgiref(self):
        url = self.converter.get_vcs("wsgiref")
        self.assertInsensitiveEqual(url, "http://svn.eby-sarna.com/wsgiref/")

    def test_s3cmd(self):
        url = self.converter.get_vcs("s3cmd")
        self.assertInsensitiveEqual(url, "https://github.com/s3tools/s3cmd")

    def test_tinys3(self):
        url = self.converter.get_vcs("tinys3")
        self.assertInsensitiveEqual(url, "https://github.com/smore-inc/tinys3")

    def test_github_wiki_pybrain(self):
        url = self.converter.get_vcs("pybrain")
        self.assertInsensitiveEqual(url, "https://github.com/pybrain/pybrain")

    def test_roundup(self):
        url = self.converter.get_vcs("roundup")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/roundup")

    def test_aliyun_direct(self):
        url = self.converter.get_vcs("aliyun-python-sdk-core")
        self.assertInsensitiveEqual(
            url, "https://github.com/aliyun/aliyun-openapi-python-sdk"
        )

    def test_aliyun_namespace(self):
        url = self.converter.get_vcs("aliyun-python-sdk-ecs")
        self.assertInsensitiveEqual(
            url, "https://github.com/aliyun/aliyun-openapi-python-sdk"
        )

    def test_matrix_synapse_ldap3(self):
        url = self.converter.get_vcs("matrix-synapse-ldap3")
        self.assertInsensitiveEqual(
            url, "https://github.com/matrix-org/matrix-synapse-ldap3"
        )

    def test_galaxy_lib(self):
        url = self.converter.get_vcs("galaxy_lib")
        self.assertInsensitiveEqual(url, "https://github.com/galaxyproject/galaxy-lib")

    def test_theme_exclusion_sphinx_rtd_theme(self):
        url = self.converter.get_vcs("sphinx_rtd_theme")
        self.assertInsensitiveEqual(url, "https://github.com/rtfd/sphinx_rtd_theme")
        # redirects to https://github.com/readthedocs/sphinx_rtd_theme

    def test_theme_exclusion_alabaster(self):
        url = self.converter.get_vcs("alabaster")
        self.assertInsensitiveEqual(url, "https://github.com/bitprophet/alabaster")

    def test_trac_xml2rfc(self):
        url = self.converter.get_vcs("xml2rfc")
        self.assertEqual(url, "https://trac.tools.ietf.org/tools/xml2rfc")

    def test_mhash(self):
        url = self.converter.get_vcs("python-mhash")
        # mhash has zero assets
        self.assertEqual(url, "https://sourceforge.net/projects/mhash")

    def test_logbook(self):
        url = self.converter.get_vcs("Logbook")
        self.assertEqual(url, "https://github.com/getlogbook/logbook")

    def test_Pyrex(self):
        url = self.converter.get_vcs("Pyrex")
        self.assertInsensitiveEqual(
            url, "https://www.csse.canterbury.ac.nz/greg.ewing/python/Pyrex/"
        )
        # hg repo at https://www.csse.canterbury.ac.nz/greg.ewing/python/Pyrex/hg/

    def test_tryton_GooCalendar(self):
        url = self.converter.get_vcs("GooCalendar")
        self.assertEqual(url, "https://hg.tryton.org/goocalendar")

    def test_Cython(self):
        url = self.converter.get_vcs("Cython")
        self.assertEqual(url, "https://github.com/cython/cython")

    def test_bpython(self):
        url = self.converter.get_vcs("bpython")
        self.assertEqual(url, "https://github.com/bpython/bpython")

    def test_pygal(self):
        url = self.converter.get_vcs("pygal")
        self.assertEqual(url, "https://github.com/Kozea/pygal")

    def test_amqpstorm(self):
        url = self.converter.get_vcs("amqpstorm")
        self.assertEqual(url, "https://github.com/eandersson/amqpstorm")

    def test_diskcache(self):
        url = self.converter.get_vcs("diskcache")
        self.assertEqual(url, "https://github.com/grantjenks/python-diskcache")

    def test_editdistance(self):
        url = self.converter.get_vcs("editdistance")
        self.assertEqual(url, "https://github.com/aflc/editdistance")

    def test_ftputil(self):
        url = self.converter.get_vcs("ftputil")
        self.assertInsensitiveEqual(url, "https://ftputil.sschwarzer.net/")

    def test_junos_eznc(self):
        url = self.converter.get_vcs("junos-eznc")
        self.assertInsensitiveEqual(url, "https://github.com/Juniper/py-junos-eznc")

    def test_logilab_astng(self):
        url = self.converter.get_vcs("logilab-astng")
        self.assertInsensitiveEqual(
            url, "https://www.logilab.org/project/logilab-astng"
        )

    def test_logilab_common(self):
        url = self.converter.get_vcs("logilab-common")
        self.assertInsensitiveEqual(
            url, "https://www.logilab.org/project/logilab-common"
        )

    def test_logreduce(self):
        # https://github.com/jayvdb/pypidb/issues/46
        url = self.converter.get_vcs("logreduce")
        self.assertInsensitiveEqual(
            url, "https://softwarefactory-project.io/cgit/logreduce"
        )

    def test_Unidecode(self):
        url = self.converter.get_vcs("Unidecode")
        self.assertInsensitiveEqual(
            url, "https://github.com/avian2/unidecode"
        )  # https://www.tablix.org/~avian/git/unidecode.git

    def test_musicbrainzngs(self):
        url = self.converter.get_vcs("musicbrainzngs")
        self.assertInsensitiveEqual(
            url, "https://github.com/alastair/python-musicbrainzngs"
        )

    def test_scm_mercurial(self):
        url = self.converter.get_vcs("mercurial")
        self.assertEqual(url, "https://www.mercurial-scm.org/repo/hg")

    def test_git_scheme(self):
        url = self.converter.get_vcs("lxc-python2")
        self.assertEqual(url, "https://github.com/lxc/python2-lxc")

    def test_git_plus_https_scheme(self):
        url = self.converter.get_vcs("python-zaqarclient")
        self.assertInsensitiveEqual(
            url, "https://opendev.org/openstack/python-zaqarclient"
        )

    def test_git_scheme2(self):
        url = self.converter.get_vcs("tinysegmenter")
        self.assertEqual(url, "http://git.tuxfamily.org/tinysegmente/tinysegmenter/")

    def test_git_scheme_with_backticks(self):
        url = self.converter.get_vcs("package")
        self.assertEqual(url, "https://github.com/ingydotnet/package-py")

    def test_autobahn(self):
        url = self.converter.get_vcs("autobahn")
        self.assertInsensitiveEqual(
            url, "https://github.com/crossbario/autobahn-python"
        )

    def test_travis_svg(self):
        url = self.converter.get_vcs("dropbox")
        self.assertEqual(url, "https://github.com/dropbox/dropbox-sdk-python")

    def test_vlc(self):
        url = self.converter.get_vcs("python-vlc")
        self.assertInsensitiveEqual(
            url, "https://git.videolan.org/?p=vlc/bindings/python.git"
        )

    def test_arch_pymad(self):
        url = self.converter.get_vcs("pymad")
        self.assertEqual(url, "https://spacepants.org/src/pymad")

    def test_www_github_openid_cla(self):
        url = self.converter.get_vcs("python-openid-cla")
        self.assertEqual(url, "https://github.com/puiterwijk/python-openid-cla")

    def test_protego(self):
        url = self.converter.get_vcs("protego")
        self.assertEqual(url, "https://github.com/scrapy/protego")

    def test_dash(self):
        url = self.converter.get_vcs("dash")
        self.assertEqual(url, "https://github.com/plotly/dash")

    def test_strictyaml(self):
        url = self.converter.get_vcs("strictyaml")
        self.assertInsensitiveEqual(url, "https://github.com/crdoconnor/strictyaml")

    def test_tryton_relatorio(self):
        url = self.converter.get_vcs("relatorio")
        self.assertEqual(url, "https://hg.tryton.org/relatorio")

    def test_requests_download(self):
        url = self.converter.get_vcs("requests-download")
        self.assertEqual(url, "https://github.com/takluyver/requests_download")

    def test_rsa(self):
        url = self.converter.get_vcs("rsa")
        self.assertEqual(url, "https://github.com/sybrenstuvel/python-rsa")

    def test_tryton_sql(self):
        url = self.converter.get_vcs("python-sql")
        self.assertEqual(url, "https://hg.tryton.org/python-sql")

    def test_found_whois(self):
        url = self.converter.get_vcs("python-whois")
        self.assertEqual(url, "https://github.com/richardpenman/pywhois")

    def test_selectors2(self):
        url = self.converter.get_vcs("selectors2")
        self.assertEqual(url, "https://github.com/SethMichaelLarson/selectors2")

    def test_sgmllib3k(self):
        url = self.converter.get_vcs("sgmllib3k")
        self.assertEqual(url, "https://hg.hardcoded.net/sgmllib")

    def test_tkreadonly(self):
        url = self.converter.get_vcs("tkreadonly")
        self.assertEqual(url, "https://github.com/pybee/tkreadonly")

    def test_tmx(self):
        url = self.converter.get_vcs("tmx")
        self.assertEqual(url, "https://savannah.nongnu.org/projects/python-tmx")

    def test_yum_urlgrabber(self):
        url = self.converter.get_vcs("urlgrabber")
        self.assertEqual(url, "http://yum.baseurl.org/gitwebd27a.html?p=urlgrabber")

    def test_urwid(self):
        url = self.converter.get_vcs("urwid")
        self.assertEqual(url, "https://github.com/urwid/urwid")

    def test_wsgi_intercept(self):
        url = self.converter.get_vcs("wsgi_intercept")
        self.assertEqual(url, "https://github.com/cdent/wsgi-intercept")

    def test_scales(self):
        url = self.converter.get_vcs("scales")
        self.assertEqual(url, "https://github.com/Cue/scales")

    def test_pymetar(self):
        url = self.converter.get_vcs("pymetar")
        self.assertEqual(url, "https://github.com/klausman/pymetar")

    def test_future(self):
        url = self.converter.get_vcs("future")
        self.assertEqual(url, "https://github.com/PythonCharmers/python-future")

    def test_kaitaistruct(self):
        url = self.converter.get_vcs("kaitaistruct")
        self.assertEqual(url, "https://github.com/kaitai-io/kaitai_struct")
        # actually git submodule https://github.com/kaitai-io/kaitai_struct_python_runtime

    def test_rfc3986(self):
        url = self.converter.get_vcs("rfc3986")
        self.assertInsensitiveEqual(url, "https://github.com/sigmavirus24/rfc3986")
        # redirects to https://github.com/python-hyper/rfc3986

    def test_rfc3987(self):
        url = self.converter.get_vcs("rfc3987")
        self.assertInsensitiveEqual(url, "https://github.com/dgerber/rfc3987")

    def test_Chameleon(self):
        url = self.converter.get_vcs("Chameleon")
        self.assertInsensitiveEqual(url, "https://github.com/malthe/chameleon")

    def test_Genshi(self):
        url = self.converter.get_vcs("Genshi")
        self.assertInsensitiveEqual(url, "https://github.com/edgewall/genshi")

    def test_M2Crypto(self):
        url = self.converter.get_vcs("M2Crypto")
        self.assertInsensitiveEqual(url, "https://gitlab.com/m2crypto/m2crypto")

    def test_twine(self):
        url = self.converter.get_vcs("twine")
        self.assertInsensitiveEqual(url, "https://github.com/pypa/twine")

    def test_WebTest(self):
        url = self.converter.get_vcs("WebTest")
        self.assertInsensitiveEqual(url, "https://github.com/Pylons/webtest")

    def test_pygithub(self):
        url = self.converter.get_vcs("pygithub")
        self.assertInsensitiveEqual(url, "https://github.com/pygithub/pygithub")

    def test_github3py(self):
        url = self.converter.get_vcs("github3.py")
        self.assertInsensitiveEqual(url, "https://github.com/sigmavirus24/github3.py")

    def test_apache_org(self):
        url = self.converter.get_vcs("avro")
        self.assertInsensitiveEqual(url, "https://github.com/apache/avro")

    def test_githubusercontent(self):
        url = self.converter.get_vcs("Kivy")
        self.assertInsensitiveEqual(url, "https://github.com/kivy/kivy")

    def test_github_io_reject(self):
        url = self.converter.get_vcs("IMDbPY")
        self.assertInsensitiveEqual(url, "https://github.com/alberanid/imdbpy")

    def test_github_io_accept(self):
        url = self.converter.get_vcs("acitoolkit")
        self.assertInsensitiveEqual(url, "https://github.com/datacenter/acitoolkit")

    def test_ghbtns_com(self):
        url = self.converter.get_vcs("invoke")
        self.assertInsensitiveEqual(url, "https://github.com/pyinvoke/invoke")

    def test_codecov_io(self):
        url = self.converter.get_vcs("multidict")
        self.assertInsensitiveEqual(url, "https://github.com/aio-libs/multidict")

    def test_unittest2(self):
        url = self.converter.get_vcs("unittest2")
        self.assertInsensitiveEqual(url, "https://hg.python.org/unittest2")

    def test_heapdict(self):
        url = self.converter.get_vcs("heapdict")
        self.assertInsensitiveEqual(url, "https://github.com/DanielStutzbach/heapdict")

    def test_keyczar(self):
        url = self.converter.get_vcs("python-keyczar")
        self.assertInsensitiveEqual(url, "https://github.com/google/keyczar")

    def test_dateutil(self):
        url = self.converter.get_vcs("python-dateutil")
        self.assertInsensitiveEqual(url, "https://github.com/dateutil/dateutil")

    def test_invocations(self):
        url = self.converter.get_vcs("invocations")
        self.assertInsensitiveEqual(url, "https://github.com/pyinvoke/invocations")

    def test_gitorious_org_oset(self):
        url = self.converter.get_vcs("oset")
        self.assertInsensitiveEqual(url, "http://gitorious.org/sleipnir/python-oset")

    def test_celery_kombu(self):
        url = self.converter.get_vcs("kombu")
        self.assertInsensitiveEqual(url, "https://github.com/celery/kombu")

    def test_lftools(self):
        url = self.converter.get_vcs("lftools")
        self.assertInsensitiveEqual(
            url, "https://gerrit.linuxfoundation.org/infra/q/project:releng%252Flftools"
        )

    def test_custom_host_bsddb3(self):
        url = self.converter.get_vcs("bsddb3")
        self.assertInsensitiveEqual(url, "https://hg.jcea.es/pybsddb")

    def test_sf_net_crcmod(self):
        url = self.converter.get_vcs("crcmod")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/crcmod")

    def test_sf_net_expanded_docutils(self):
        url = self.converter.get_vcs("docutils")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/docutils")

    def test_ZSI(self):
        url = self.converter.get_vcs("ZSI")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/pywebsvcs")

    def test_ignore_sf_djvulibre(self):
        url = self.converter.get_vcs("python-djvulibre")
        self.assertInsensitiveEqual(url, "https://github.com/jwilk/python-djvulibre")

    def test_pycdio(self):
        url = self.converter.get_vcs("pycdio")
        self.assertInsensitiveEqual(
            url, "http://git.savannah.gnu.org/cgit/libcdio/pycdio.git"
        )

    def test_webpy(self):
        url = self.converter.get_vcs("web.py")
        self.assertInsensitiveEqual(url, "https://github.com/webpy/webpy")

    def test_spark_parser(self):
        url = self.converter.get_vcs("spark-parser")
        self.assertInsensitiveEqual(url, "https://github.com/rocky/python-spark")

    def test_tagpy(self):
        url = self.converter.get_vcs("tagpy")
        self.assertInsensitiveEqual(url, "http://git.tiker.net/?p=tagpy.git")

    def test_git_plus_https_asyncssh(self):
        url = self.converter.get_vcs("asyncssh")
        self.assertInsensitiveEqual(url, "https://github.com/ronf/asyncssh")

    def test_catkin_pkg(self):
        url = self.converter.get_vcs("catkin-pkg")
        self.assertInsensitiveEqual(
            url, "https://github.com/ros-infrastructure/catkin_pkg"
        )

    def test_imagecodecs(self):
        url = self.converter.get_vcs("imagecodecs")
        self.assertInsensitiveEqual(url, "https://github.com/cgohlke/imagecodecs")

    def test_podcastparser(self):
        url = self.converter.get_vcs("podcastparser")
        self.assertInsensitiveEqual(url, "https://github.com/gpodder/podcastparser")

    def test_pluggy(self):
        url = self.converter.get_vcs("pluggy")
        self.assertInsensitiveEqual(url, "https://github.com/pytest-dev/pluggy")

    def test_debian(self):
        url = self.converter.get_vcs("python-debian")
        self.assertInsensitiveEqual(
            url, "https://salsa.debian.org/python-debian-team/python-debian"
        )

    def test_nxapi_plumbing(self):
        url = self.converter.get_vcs("nxapi-plumbing")
        self.assertInsensitiveEqual(url, "https://github.com/ktbyers/nxapi-plumbing")

    def test_proboscis(self):
        url = self.converter.get_vcs("proboscis")
        self.assertInsensitiveEqual(
            url, "https://github.com/rackerlabs/python-proboscis"
        )

    def test_pysndfile(self):
        url = self.converter.get_vcs("pysndfile")
        self.assertInsensitiveEqual(url, "https://forge-2.ircam.fr/roebel/pysndfile")

    def test_coveralls_check(self):
        url = self.converter.get_vcs("coveralls-check")
        self.assertInsensitiveEqual(url, "https://github.com/cjw296/coveralls-check")

    def test_MarkupSafe(self):
        url = self.converter.get_vcs("MarkupSafe")
        self.assertInsensitiveEqual(url, "https://github.com/pallets/MarkupSafe")

    def test_pygraphviz(self):
        url = self.converter.get_vcs("pygraphviz")
        self.assertInsensitiveEqual(url, "https://github.com/pygraphviz/pygraphviz")

    def test_jsonpickle(self):
        url = self.converter.get_vcs("jsonpickle")
        self.assertInsensitiveEqual(url, "https://github.com/jsonpickle/jsonpickle")

    def test_django_oot(self):
        url = self.converter.get_vcs("django-oot")
        self.assertInsensitiveEqual(url, "http://tracpub.yaco.es/djangoapps/wiki/OOT")

    def test_django_oauth(self):
        url = self.converter.get_vcs("django-oauth")
        self.assertInsensitiveEqual(url, "http://code.welldev.org/django-oauth/")

    def test_oauth_provider(self):
        url = self.converter.get_vcs("oauth_provider")
        self.assertInsensitiveEqual(url, "http://code.welldev.org/django-oauth/")

    def test_django_oauth_plus(self):
        url = self.converter.get_vcs("django-oauth-plus")
        self.assertInsensitiveEqual(
            url, "https://bitbucket.org/david/django-oauth-plus"
        )

    def test_moneta(self):
        url = self.converter.get_vcs("moneta")
        self.assertInsensitiveEqual(url, "https://github.com/d9pouces/Moneta")

    def test_github_octolytics(self):
        url = self.converter.get_vcs("github_octolytics")
        self.assertInsensitiveEqual(
            url, "https://github.com/andrewp-as-is/github-octolytics.py"
        )

    def test_qpid_proton(self):
        url = self.converter.get_vcs("python-qpid-proton")
        self.assertInsensitiveEqual(url, "https://github.com/apache/qpid-proton")

    def test_DeCiDa(self):
        url = self.converter.get_vcs("DeCiDa")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/decida")

    def test_sf_net_trac_AllPairs(self):
        url = self.converter.get_vcs("AllPairs")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/allpairs")

    def test_requests_threads(self):
        url = self.converter.get_vcs("requests-threads")
        self.assertInsensitiveEqual(url, "https://github.com/requests/requests-threads")

    def test_openmesh(self):
        url = self.converter.get_vcs("openmesh")
        self.assertInsensitiveEqual(
            url, "https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python"
        )

    def test_threevis(self):
        url = self.converter.get_vcs("threevis")
        self.assertInsensitiveEqual(
            url, "https://www.graphics.rwth-aachen.de:9000/threevis/threevis"
        )

    def test_linaro(self):
        url = self.converter.get_vcs("django-restricted-resource")
        self.assertInsensitiveEqual(
            url, "https://git.linaro.org/lava/django-restricted-resource.git"
        )

    def test_wmi(self):
        url = self.converter.get_vcs("wmi")
        self.assertInsensitiveEqual(url, "https://github.com/tjguk/wmi")

    def test_pywin32(self):
        url = self.converter.get_vcs("pywin32")
        self.assertInsensitiveEqual(url, "https://github.com/mhammond/pywin32")

    def test_waiting(self):
        url = self.converter.get_vcs("waiting")
        self.assertInsensitiveEqual(url, "https://github.com/vmalloc/waiting")

    def test_flux(self):
        url = self.converter.get_vcs("flux")
        self.assertInsensitiveEqual(url, "https://github.com/vmalloc/flux")

    def test_flex(self):
        url = self.converter.get_vcs("flex")
        self.assertInsensitiveEqual(url, "https://github.com/pipermerriam/flex")

    def test_awscli(self):
        url = self.converter.get_vcs("awscli")
        self.assertInsensitiveEqual(url, "https://github.com/aws/aws-cli")

    def test_pep8(self):
        url = self.converter.get_vcs("pep8")
        self.assertInsensitiveEqual(url, "https://github.com/pycqa/pep8")

    def test_igraph(self):
        url = self.converter.get_vcs(
            "python-igraph"
        )  # not http://www.lfd.uci.edu/~gohlke/pythonlibs
        self.assertInsensitiveEqual(url, "https://github.com/igraph/python-igraph")

    def test_gsutil(self):
        url = self.converter.get_vcs("gsutil")
        self.assertInsensitiveEqual(
            url, "https://github.com/GoogleCloudPlatform/gsutil"
        )

    def test_requests_toolbelt(self):
        url = self.converter.get_vcs("requests-toolbelt")
        self.assertInsensitiveEqual(url, "https://github.com/requests/toolbelt")

    def test_snowplow_tracker(self):
        url = self.converter.get_vcs("snowplow-tracker")
        self.assertInsensitiveEqual(
            url, "https://github.com/snowplow/snowplow-python-tracker"
        )

    def test_snowplow_tracker_minimal(self):
        url = self.converter.get_vcs("minimal-snowplow-tracker")
        self.assertInsensitiveEqual(
            url, "https://github.com/fishtown-analytics/snowplow-python-tracker"
        )

    def test_Schevo(self):
        url = self.converter.get_vcs("Schevo")
        self.assertInsensitiveEqual(url, "https://github.com/11craft/schevo")

    def test_SchevoDurus(self):
        url = self.converter.get_vcs("SchevoDurus")
        self.assertInsensitiveEqual(url, "https://github.com/11craft/schevodurus")

    def test_SchevoGears(self):
        url = self.converter.get_vcs("SchevoGears")
        self.assertInsensitiveEqual(url, "https://github.com/11craft/schevogears")

    def test_SchevoSql(self):
        url = self.converter.get_vcs("SchevoSql")
        self.assertInsensitiveEqual(url, "https://github.com/11craft/schevosql")

    def test_publicsuffix2(self):
        url = self.converter.get_vcs("publicsuffix2")
        self.assertInsensitiveEqual(url, "https://github.com/nexb/python-publicsuffix2")

    def test_publicsuffixlist(self):
        url = self.converter.get_vcs("publicsuffixlist")
        self.assertInsensitiveEqual(url, "https://github.com/ko-zu/psl")

    def test_pattern(self):
        url = self.converter.get_vcs("pattern")
        self.assertInsensitiveEqual(url, "https://github.com/clips/pattern")

    def test_pip(self):
        url = self.converter.get_vcs("pip")
        self.assertInsensitiveEqual(url, "https://github.com/pypa/pip")

    def test_pipfile(self):
        url = self.converter.get_vcs("pipfile")
        self.assertInsensitiveEqual(url, "https://github.com/pypa/pipfile")

    def test_geopandas(self):
        url = self.converter.get_vcs("geopandas")
        self.assertEqual(url, "https://github.com/geopandas/geopandas")

    def test_upt(self):
        url = self.converter.get_vcs("upt")
        self.assertEqual(url, "https://framagit.org/upt/upt")

    def test_upt_pypi(self):
        url = self.converter.get_vcs("upt-pypi")
        self.assertEqual(url, "https://framagit.org/upt/upt-pypi")

    def test_flup(self):
        url = self.converter.get_vcs("flup")
        self.assertEqual(url, "https://www.saddi.com/software/flup/")


class TestEmail(_TestBase):
    def test_sympy(self):
        url = self.converter.get_vcs("sympy")
        self.assertInsensitiveEqual(url, "https://github.com/sympy/sympy")

    def test_pypowervm(self):
        url = self.converter.get_vcs("pypowervm")
        self.assertInsensitiveEqual(url, "https://github.com/powervm/pypowervm")

    def test_sigopt(self):
        url = self.converter.get_vcs("sigopt")
        self.assertInsensitiveEqual(url, "https://github.com/sigopt/sigopt-python")

    def test_veusz(self):
        url = self.converter.get_vcs("veusz")
        self.assertInsensitiveEqual(url, "https://github.com/veusz/veusz")

    def test_pystemmer(self):
        url = self.converter.get_vcs("pystemmer")
        self.assertInsensitiveEqual(url, "https://github.com/snowballstem/pystemmer")

    def test_medusa(self):
        url = self.converter.get_vcs("medusa")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/oedipus")

    def test_igor(self):
        url = self.converter.get_vcs("igor")
        self.assertInsensitiveEqual(url, "http://git.tremily.us/?p=igor.git")


class TestOfflineWeb(_TestBase):
    def test_potr(self):
        url = self.converter.get_vcs("python-potr")
        self.assertInsensitiveEqual(url, "https://github.com/afflux/pure-python-otr")


class TestWeighting(_TestBase):
    def test_pyload(self):
        url = self.converter.get_vcs("pyload-ng")
        self.assertEqual(url, "https://github.com/pyload/pyload")

    def test_featureflow(self):
        url = self.converter.get_vcs("featureflow")
        self.assertEqual(url, "https://github.com/JohnVinyard/featureflow")


class TestSimilarity(_TestBase):
    def test_pycli(self):
        url = self.converter.get_vcs("pycli")
        self.assertEqual(url, "https://github.com/whilp/cli")

    def test_mygpoclient(self):
        url = self.converter.get_vcs("mygpoclient")
        self.assertInsensitiveEqual(url, "https://github.com/gpodder/mygpoclient")

    def test_agate_excel(self):
        url = self.converter.get_vcs("agate-excel")
        self.assertInsensitiveEqual(url, "https://github.com/wireservice/agate-excel")

    def test_sst(self):
        url = self.converter.get_vcs("sst")
        self.assertInsensitiveEqual(url, "https://launchpad.net/selenium-simple-test")

    def test_boxsdk(self):
        url = self.converter.get_vcs("boxsdk")
        self.assertInsensitiveEqual(url, "https://github.com/box/box-python-sdk")


class TestMulti(_TestBase):
    def test_bytecodeassembler(self):
        url = self.converter.get_vcs("BytecodeAssembler")
        self.assertInsensitiveEqual(
            url, "https://github.com/peak-legacy/bytecodeassembler"
        )
        # Was "http://svn.eby-sarna.com/BytecodeAssembler/"

    def test_peak(self):
        url = self.converter.get_vcs("PEAK")
        self.assertInsensitiveEqual(url, "https://github.com/peak-legacy/peak")
        # Was "http://svn.eby-sarna.com/PEAK/"

    def test_oslo_vmware(self):
        url = self.converter.get_vcs("oslo-vmware")
        self.assertInsensitiveEqual(url, "https://opendev.org/openstack/oslo.vmware")

    def test_oslo_upgradecheck(self):
        url = self.converter.get_vcs("oslo-upgradecheck")
        self.assertInsensitiveEqual(
            url, "https://opendev.org/openstack/oslo.upgradecheck"
        )

    def test_drfdocs(self):
        url = self.converter.get_vcs("drfdocs")
        self.assertInsensitiveEqual(
            url, "https://github.com/manosim/django-rest-framework-docs"
        )

    def test_uritemplate(self):
        url = self.converter.get_vcs("uritemplate-py")
        self.assertInsensitiveEqual(url, "https://github.com/python-hyper/uritemplate")

    def test_category_encoders(self):
        url = self.converter.get_vcs("category-encoders")
        self.assertInsensitiveEqual(
            url, "https://github.com/scikit-learn-contrib/categorical-encoding"
        )

    def test_google_api_core(self):
        url = self.converter.get_vcs("google-api-core")
        self.assertInsensitiveEqual(
            url, "https://github.com/googleapis/google-cloud-python"
        )

    def test_googleapis_common_protos(self):
        url = self.converter.get_vcs("googleapis-common-protos")
        self.assertInsensitiveEqual(url, "https://github.com/googleapis/googleapis")

    def test_lecli(self):
        url = self.converter.get_vcs("logentries-lecli")
        self.assertInsensitiveEqual(url, "https://github.com/logentries/lecli")

    def test_pyload_ng(self):
        url = self.converter.get_vcs("pyload-ng")
        self.assertInsensitiveEqual(url, "https://github.com/pyload/pyload")
        # also mirrored to "https://gitlab.com/pyload/pyload"
