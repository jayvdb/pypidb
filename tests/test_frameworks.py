from pypidb._pypi import InvalidPackage, PackageWithoutUrls
from tests.utils import _TestBase


class TestAntlr(_TestBase):
    def test_antlr_3(self):
        url = self.converter.get_vcs("antlr-python-runtime")
        self.assertInsensitiveEqual(url, "https://github.com/antlr/antlr3")

    def test_antlr3_hyphen(self):
        url = self.converter.get_vcs("antlr3-python-runtime")
        self.assertInsensitiveEqual(url, "https://github.com/antlr/antlr3")

    def test_antlr3_underscore(self):
        url = self.converter.get_vcs("antlr3_python_runtime")
        self.assertInsensitiveEqual(url, "https://github.com/antlr/antlr3")

    def test_antlr4(self):
        url = self.converter.get_vcs("antlr4-python3-runtime")
        self.assertInsensitiveEqual(url, "https://github.com/antlr/antlr4")

    def test_antlr4python3runtime(self):
        self.assertRaisesNoUrls("antlr4python3runtime")


class TestGRPC(_TestBase):
    def test_grpc(self):
        url = self.converter.get_vcs("grpc")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/seewind/grpc")

    def test_grpcio(self):
        url = self.converter.get_vcs("grpcio")
        self.assertInsensitiveEqual(url, "https://github.com/grpc/grpc")

    def test_grpcio_tools(self):
        url = self.converter.get_vcs("grpcio-tools")
        self.assertInsensitiveEqual(url, "https://github.com/grpc/grpc")

    def test_grpcio_testing(self):
        url = self.converter.get_vcs("grpcio-testing")
        self.assertInsensitiveEqual(url, "https://github.com/grpc/grpc")

    def test_grpcio_reflection(self):
        url = self.converter.get_vcs("grpcio-reflection")
        self.assertInsensitiveEqual(url, "https://github.com/grpc/grpc")

    def test_grpcio_status(self):
        url = self.converter.get_vcs("grpcio-status")
        self.assertInsensitiveEqual(url, "https://github.com/grpc/grpc")

    def test_grpcio_health_checking(self):
        url = self.converter.get_vcs("grpcio-health-checking")
        self.assertInsensitiveEqual(url, "https://github.com/grpc/grpc")

    def test_grpcio_tests(self):
        with self.assertRaises(InvalidPackage):
            self.converter.get_vcs("grpcio-tests")

    def test_grpcio_gcp(self):
        url = self.converter.get_vcs("grpcio-gcp")
        self.assertInsensitiveEqual(
            url, "https://github.com/GoogleCloudPlatform/grpc-gcp-python"
        )

    def test_grpcio_opentracing(self):
        # https://github.com/opentracing-contrib/python-grpc/pull/27
        url = self.converter.get_vcs("grpcio-opentracing")
        self.assertInsensitiveEqual(
            url, "https://github.com/opentracing-contrib/python-grpc"
        )


class TestBuildbot(_TestBase):
    def test_buildbot(self):
        url = self.converter.get_vcs("buildbot")
        self.assertInsensitiveEqual(url, "https://github.com/buildbot/buildbot")

    def test_buildbot_worker(self):
        url = self.converter.get_vcs("buildbot-worker")
        self.assertInsensitiveEqual(url, "https://github.com/buildbot/buildbot")

    def test_buildbot_slave(self):
        # slave was renamed to worker
        url = self.converter.get_vcs("buildbot-slave")
        self.assertInsensitiveEqual(url, "https://github.com/buildbot/buildbot")


class TestZope(_TestBase):
    def test_zope(self):
        url = self.converter.get_vcs("zope")
        self.assertInsensitiveEqual(url, "https://github.com/zopefoundation/Zope")

    def test_zc(self):
        with self.assertRaises(InvalidPackage):
            self.converter.get_vcs("zc")

    def test_z3c(self):
        with self.assertRaises(InvalidPackage):
            self.converter.get_vcs("z3c")

    def test_zope_testing(self):
        url = self.converter.get_vcs("zope.testing")
        self.assertEqual(url, "https://github.com/zopefoundation/zope.testing")

    def test_zdaemon(self):
        url = self.converter.get_vcs("zdaemon")
        self.assertEqual(url, "https://github.com/zopefoundation/zdaemon")

    def test_zc_zdaemonrecipe(self):
        url = self.converter.get_vcs("zc.zdaemonrecipe")
        self.assertEqual(url, "https://github.com/zopefoundation/zc.zdaemonrecipe")

    def test_zc_recipe_deployment(self):
        url = self.converter.get_vcs("zc.recipe.deployment")
        self.assertEqual(url, "https://github.com/zopefoundation/zc.recipe.deployment")

    def test_zc_customdoctests(self):
        url = self.converter.get_vcs("zc.customdoctests")
        self.assertEqual(url, "https://github.com/zopefoundation/zc.customdoctests")

    def test_zc_customdoctests_hyphen(self):
        url = self.converter.get_vcs("zc-customdoctests")
        self.assertEqual(url, "https://github.com/zopefoundation/zc.customdoctests")

    def test_zc_customdoctests_underscore(self):
        url = self.converter.get_vcs("zc_customdoctests")
        self.assertEqual(url, "https://github.com/zopefoundation/zc.customdoctests")

    def test_zc_recipe_egg(self):
        url = self.converter.get_vcs("zc.recipe.egg")
        self.assertEqual(url, "https://github.com/buildout/buildout")

    def test_zc_buildout(self):
        url = self.converter.get_vcs("zc.buildout")
        self.assertEqual(url, "https://github.com/buildout/buildout")

    def test_zc_zodbrecipes(self):
        url = self.converter.get_vcs("zc.zodbrecipes")
        self.assertEqual(url, "https://github.com/zopefoundation/zc.zodbrecipes")

    def test_z3c_schema2xml(self):
        url = self.converter.get_vcs("z3c.schema2xml")
        self.assertEqual(url, "https://github.com/zopefoundation/z3c.schema2xml")

    def test_z3c_testsetup(self):
        url = self.converter.get_vcs("z3c.testsetup")
        self.assertEqual(url, "https://github.com/zopefoundation/z3c.testsetup")


class TestTurboGears(_TestBase):
    def test_turbogears_v1(self):
        url = self.converter.get_vcs("turbogears")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/turbogears1")

    def test_TurboKid(self):
        url = self.converter.get_vcs("turbokid")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/turbogears1")

    def test_turbomail(self):
        url = self.converter.get_vcs("turbomail")
        self.assertInsensitiveEqual(url, "https://github.com/marrow/marrow.mailer")
        # marrow/marrow.mailer redirects to marrow/mailer
        url = self.converter.get_vcs("marrow.mailer")
        self.assertInsensitiveEqual(url, "https://github.com/marrow/mailer")

    def test_Cheetah(self):
        url = self.converter.get_vcs("Cheetah")
        self.assertInsensitiveEqual(url, "https://github.com/cheetahtemplate/cheetah")

    def test_Cheetah3(self):
        url = self.converter.get_vcs("Cheetah3")
        self.assertInsensitiveEqual(url, "https://github.com/CheetahTemplate3/cheetah3")

    def test_TurboCheetah(self):
        url = self.converter.get_vcs("TurboCheetah")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/turbogears1")

    def test_turbogears_v2(self):
        url = self.converter.get_vcs("turbogears2")
        self.assertInsensitiveEqual(url, "https://github.com/TurboGears/tg2")

    def test_tg_devtools(self):
        url = self.converter.get_vcs("tg.devtools")
        self.assertInsensitiveEqual(url, "https://github.com/TurboGears/tg2devtools")

    def test_sprox(self):
        url = self.converter.get_vcs("sprox")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/percious/sprox")
        # should be https://github.com/TurboGears/sprox

    def test_tgext_debugbar(self):
        url = self.converter.get_vcs("tgext.debugbar")
        self.assertInsensitiveEqual(url, "https://github.com/turbogears/tgext.debugbar")

    def test_tg_ext_silverplate(self):
        url = self.converter.get_vcs("tg.ext.silverplate")
        self.assertInsensitiveEqual(url, "https://github.com/pedersen/tgtools")
        # Should stop at https://code.google.com/p/tgtools, as github repo is empty

    def test_Catwalk(self):
        url = self.converter.get_vcs("Catwalk")
        self.assertInsensitiveEqual(url, "https://github.com/pedersen/tgtools")

    def test_tgmochikit(self):
        url = self.converter.get_vcs("tgmochikit")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/turbogears1")

    def test_tgfastdata(self):
        self.assertRaisesNoUrls("tgfastdata")
        # Probably should be https://sourceforge.net/projects/turbogears1
        # but too old to be of great concern

    def test_ToscaWidgets(self):
        # TODO: https://bitbucket.org/toscawidgets/toscawidgets
        self.assertRaisesNoUrls("ToscaWidgets")

    def test_tw2_core(self):
        url = self.converter.get_vcs("tw2.core")
        self.assertInsensitiveEqual(url, "https://github.com/toscawidgets/tw2.core")

    def test_tw_forms(self):
        self.assertRaisesNoUrls("tw.forms")
        # Need link queue chooser to get "http://bitbucket.org/toscawidgets/tw.forms"

    def test_tw_dynforms(self):
        self.assertRaisesNoUrls("tw.dynforms")
        # Need link queue chooser to get "http://bitbucket.org/toscawidgets/tw.dynforms"


class TestMozilla(_TestBase):
    # mozbase moved from github to hg.mozilla.org/mozilla-central , which is good
    # for cloning but not helpful for 'project SCM'.

    def test_mozlog(self):
        url = self.converter.get_vcs("mozlog")
        self.assertInsensitiveEqual(
            url, "https://wiki.mozilla.org/Auto-tools/Projects/Mozbase"
        )

    def test_mozrunner(self):
        url = self.converter.get_vcs("mozrunner")
        self.assertInsensitiveEqual(
            url, "https://wiki.mozilla.org/Auto-tools/Projects/Mozbase"
        )

    def test_nss(self):
        url = self.converter.get_vcs("python-nss")
        self.assertInsensitiveEqual(url, "https://hg.mozilla.org/projects/python-nss")

    def _test_marionette_driver(self):
        url = self.converter.get_vcs("marionette-driver")
        self.assertInsensitiveEqual(
            url, "https://wiki.mozilla.org/Auto-tools/Projects/Marionette"
        )
        # vcs is https://hg.mozilla.org/mozilla-central/file/tip/testing/marionette/client


class TestSTScI(_TestBase):
    def test_relic(self):
        url = self.converter.get_vcs("relic")
        self.assertInsensitiveEqual(url, "https://github.com/spacetelescope/relic")

    def test_stscipython(self):
        self.assertRaisesNoUrls("stscipython")

    def test_pyraf(self):
        url = self.converter.get_vcs("pyraf")
        self.assertInsensitiveEqual(url, "https://github.com/spacetelescope/pyraf")

    def test_drizzlepac(self):
        url = self.converter.get_vcs("drizzlepac")
        self.assertInsensitiveEqual(url, "https://github.com/spacetelescope/drizzlepac")

    def _test_hstcal(self):
        # Not on pypi
        url = self.converter.get_vcs("hstcal")
        self.assertInsensitiveEqual(url, "https://github.com/spacetelescope/hstcal")

    def test_stsci_sphinxext(self):
        url = self.converter.get_vcs("stsci.sphinxext")
        self.assertInsensitiveEqual(
            url, "https://github.com/spacetelescope/stsci.sphinxext"
        )

    def test_stsci_distutils(self):
        url = self.converter.get_vcs("stsci.distutils")
        self.assertInsensitiveEqual(
            url, "https://github.com/spacetelescope/stsci.distutils"
        )

    def test_PyFITS(self):
        url = self.converter.get_vcs("PyFITS")
        self.assertInsensitiveEqual(url, "https://github.com/spacetelescope/PyFITS")


class TestXStatic(_TestBase):
    def test_openstack_jquery_tablesorter(self):
        url = self._get_scm("XStatic-JQuery-TableSorter")
        self.assertInsensitiveEqual(
            url, "https://github.com/openstack/XStatic-JQuery.TableSorter"
        )

    def test_takluyver_term_dot_js(self):
        url = self._get_scm("XStatic-term.js")
        self.assertInsensitiveEqual(url, "https://github.com/takluyver/XStatic-termjs")

    def test_ThomasWaldmann_jquery_ui(self):
        url = self._get_scm("XStatic-jquery-ui")
        self.assertInsensitiveEqual(
            url, "https://github.com/xstatic-py/xstatic-jquery_ui"
        )

    def test_r1chardj0n3s_smart_table(self):
        url = self._get_scm("XStatic-smart-table")
        self.assertInsensitiveEqual(
            url, "https://github.com/r1chardj0n3s/xstatic-smart-table"
        )

    def test_dmsimard_patternfly(self):
        url = self._get_scm("XStatic-patternfly")
        self.assertInsensitiveEqual(url, "https://github.com/python-xstatic/patternfly")

    def test_dmsimard_objectpath(self):
        url = self._get_scm("XStatic-objectpath")
        self.assertInsensitiveEqual(
            url, "https://github.com/dmsimard/python-XStatic-objectpath-distgit"
        )

    def test_dmsimard_tv4(self):
        url = self._get_scm("XStatic-tv4")
        self.assertInsensitiveEqual(
            url, "https://github.com/dmsimard/python-XStatic-tv4-distgit"
        )

    def test_dmsimard_Angular_Schema_Form(self):
        url = self._get_scm("XStatic-Angular-Schema-Form")
        self.assertInsensitiveEqual(
            url,
            "https://github.com/dmsimard/python-XStatic-angular-schema-form-distgit",
        )

    def test_Spin(self):
        url = self._get_scm("XStatic-Spin")
        self.assertInsensitiveEqual(url, "https://github.com/openstack/XStatic-spin")

    def test_jquery_quicksearch(self):
        url = self._get_scm("XStatic-jquery-quicksearch")
        self.assertInsensitiveEqual(
            url, "https://github.com/openstack/xstatic-jquery.quicksearch"
        )


class TestSphinx(_TestBase):
    def test_sphinx(self):
        url = self.converter.get_vcs("sphinx")
        self.assertEqual(url, "https://github.com/sphinx-doc/sphinx")

    def test_sphinxcontrib_programoutput(self):
        url = self.converter.get_vcs("sphinxcontrib-programoutput")
        self.assertInsensitiveEqual(
            url, "https://github.com/NextThought/sphinxcontrib-programoutput"
        )

    def test_sphinxcontrib_openapi(self):
        url = self.converter.get_vcs("sphinxcontrib-openapi")
        self.assertEqual(url, "https://github.com/ikalnytskyi/sphinxcontrib-openapi")

    def test_sphinxcontrib_versioning(self):
        url = self.converter.get_vcs("sphinxcontrib-versioning")
        self.assertEqual(url, "https://github.com/Robpol86/sphinxcontrib-versioning")

    def test_sphinxcontrib_plantuml(self):
        url = self.converter.get_vcs("sphinxcontrib-plantuml")
        self.assertEqual(url, "https://github.com/sphinx-contrib/plantuml")

    def test_sphinxcontrib_napoleon(self):
        url = self.converter.get_vcs("sphinxcontrib-napoleon")
        self.assertInsensitiveEqual(url, "https://github.com/sphinx-contrib/napoleon")

    def test_sphinxcontrib_domaintools(self):
        url = self.converter.get_vcs("sphinxcontrib-domaintools")
        self.assertEqual(url, "https://bitbucket.org/klorenz/sphinxcontrib-domaintools")

    def test_sphinxcontrib_images(self):
        url = self.converter.get_vcs("sphinxcontrib-images")
        self.assertEqual(url, "https://github.com/sphinx-contrib/images")

    def test_sphinxcontrib_youtube(self):
        url = self.converter.get_vcs("sphinxcontrib-youtube")
        self.assertEqual(url, "https://github.com/shomah4a/sphinxcontrib.youtube")

    def test_sphinxcontrib_proof(self):
        url = self.converter.get_vcs("sphinxcontrib-proof")
        self.assertEqual(url, "https://framagit.org/spalax/sphinxcontrib-proof")

    def test_sphinxcontrib_spelling(self):
        url = self.converter.get_vcs("sphinxcontrib-spelling")
        self.assertEqual(url, "https://github.com/sphinx-contrib/spelling")

    def test_sphinxcontrib_restbuilder(self):
        url = self.converter.get_vcs("sphinxcontrib-restbuilder")
        self.assertEqual(url, "https://github.com/sphinx-contrib/restbuilder")

    def test_sphinxcontrib_runcmd(self):
        url = self.converter.get_vcs("sphinxcontrib-runcmd")
        self.assertEqual(url, "https://github.com/invenia/sphinxcontrib-runcmd")

    def test_sphinxcontrib_collations(self):
        with self.assertRaises(InvalidPackage):
            self.converter.get_vcs("sphinxcontrib-collations")

    def test_sphinxcontrib_websupport(self):
        url = self.converter.get_vcs("sphinxcontrib-websupport")
        self.assertEqual(url, "https://github.com/sphinx-doc/sphinxcontrib-websupport")

    def test_sphinxcontrib_applehelp(self):
        url = self.converter.get_vcs("sphinxcontrib-applehelp")
        self.assertInsensitiveEqual(
            url, "https://github.com/sphinx-doc/sphinxcontrib-applehelp"
        )

    def test_sphinxcontrib_infrae(self):
        self.assertRaisesNoUrls("sphinxcontrib-infrae")

    def test_sphinxcontrib_whoosh(self):
        # https://github.com/sphinx-contrib/whooshindex
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("sphinxcontrib-whoosh")

    def test_sphinxcontrib_gruffygen(self):
        # https://github.com/hhatto/sphinxcontrib-gruffygen
        with self.assertRaises(PackageWithoutUrls):
            self.converter.get_vcs("sphinxcontrib-gruffygen")

    def test_sphinxcontrib_devhelp(self):
        url = self.converter.get_vcs("sphinxcontrib-devhelp")
        self.assertEqual(url, "https://github.com/sphinx-doc/sphinxcontrib-devhelp")

    def test_sphinxcontrib_htmlhelp(self):
        url = self.converter.get_vcs("sphinxcontrib-htmlhelp")
        self.assertEqual(url, "https://github.com/sphinx-doc/sphinxcontrib-htmlhelp")

    def test_sphinxcontrib_jsmath(self):
        url = self.converter.get_vcs("sphinxcontrib-jsmath")
        self.assertEqual(url, "https://github.com/sphinx-doc/sphinxcontrib-jsmath")

    def test_sphinxcontrib_qthelp(self):
        url = self.converter.get_vcs("sphinxcontrib-qthelp")
        self.assertEqual(url, "https://github.com/sphinx-doc/sphinxcontrib-qthelp")

    def test_sphinxcontrib_serializinghtml(self):
        url = self.converter.get_vcs("sphinxcontrib-serializinghtml")
        self.assertEqual(
            url, "https://github.com/sphinx-doc/sphinxcontrib-serializinghtml"
        )


class TestPyPiRedirectSpin(_TestBase):
    def test_jupyter_console(self):
        # sends pypi into a spin
        # https://github.com/ionrock/cachecontrol/issues/214
        url = self.converter.get_vcs("jupyter-console")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter_console")

    def test_dot_jupyter_console(self):
        url = self.converter.get_vcs("jupyter.console")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter_console")

    def test_django_coverage_plugin(self):
        url = self.converter.get_vcs("django-coverage-plugin")
        self.assertInsensitiveEqual(
            url, "https://github.com/nedbat/django_coverage_plugin"
        )


class TestJupyter(_TestBase):
    def test_jupyter(self):
        url = self.converter.get_vcs("jupyter")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter")

    def test_jupyter_core(self):
        url = self.converter.get_vcs("jupyter-core")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter_core")

    def test_jupyter_client(self):
        url = self.converter.get_vcs("jupyter-client")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter_client")

    def _test_jupyter_console(self):
        url = self.converter.get_vcs("jupyter-console")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter_console")

    def _test_jupyter_console_underscore(self):
        url = self.converter.get_vcs("jupyter_console")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter_console")

    def test_jupyter_protocol(self):
        url = self.converter.get_vcs("jupyter-protocol")
        self.assertInsensitiveEqual(
            url, "https://github.com/takluyver/jupyter_protocol"
        )

    def test_jupyter_server(self):
        url = self.converter.get_vcs("jupyter-server")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter_server")

    def test_nbformat(self):
        url = self.converter.get_vcs("nbformat")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/nbformat")

    def test_jupyter_nbformat(self):
        url = self.converter.get_vcs("jupyter_nbformat")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/jupyter_nbformat")

    def test_nbdime(self):
        url = self.converter.get_vcs("nbdime")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter/nbdime")

    def test_ipython(self):
        url = self.converter.get_vcs("ipython")
        self.assertInsensitiveEqual(url, "https://github.com/ipython/ipython")

    def test_ipynb(self):
        url = self.converter.get_vcs("ipynb")
        self.assertInsensitiveEqual(url, "https://github.com/ipython/ipynb")

    def test_traitlets(self):
        url = self.converter.get_vcs("traitlets")
        self.assertInsensitiveEqual(url, "https://github.com/ipython/traitlets")

    def test_rlipython(self):
        url = self.converter.get_vcs("rlipython")
        self.assertInsensitiveEqual(url, "https://github.com/ipython/rlipython")

    def test_ipykernel(self):
        url = self.converter.get_vcs("ipykernel")
        self.assertInsensitiveEqual(url, "https://github.com/ipython/ipykernel")

    def test_ipyparallel(self):
        url = self.converter.get_vcs("ipyparallel")
        self.assertInsensitiveEqual(url, "https://github.com/ipython/ipyparallel")

    def test_ipywidgets(self):
        url = self.converter.get_vcs("ipywidgets")
        self.assertInsensitiveEqual(url, "https://github.com/ipython/ipywidgets")

    def test_ipyleaflet(self):
        url = self.converter.get_vcs("ipyleaflet")
        self.assertInsensitiveEqual(
            url, "https://github.com/jupyter-widgets/ipyleaflet"
        )

    def test_ipysheet(self):
        # https://github.com/jupyter-widgets/ipysheet
        self.assertRaisesNoUrls("ipysheet")

    def test_ipymidicontrols(self):
        url = self.converter.get_vcs("ipymidicontrols")
        self.assertInsensitiveEqual(
            url, "https://github.com/jupyter-widgets/midicontrols"
        )

    def test_traittypes(self):
        url = self.converter.get_vcs("traittypes")
        self.assertInsensitiveEqual(
            url, "https://github.com/jupyter-widgets/traittypes"
        )

    def test_sidecar(self):
        url = self.converter.get_vcs("sidecar")
        self.assertInsensitiveEqual(
            url, "https://github.com/jupyter-widgets/jupyterlab-sidecar"
        )

    def test_pythreejs(self):
        url = self.converter.get_vcs("pythreejs")
        self.assertInsensitiveEqual(url, "https://github.com/jupyter-widgets/pythreejs")

    def test_ipywidgets_server(self):
        # https://github.com/pbugnion/ipywidgets_server
        self.assertRaisesNoUrls("ipywidgets_server")

    def test_jupyter_singleton(self):
        url = self.converter.get_vcs("jupyter-singleton")
        self.assertInsensitiveEqual(
            url, "https://github.com/EricMende/jupyter_singleton"
        )

    def test_jupyter_pip(self):
        url = self.converter.get_vcs("jupyter-pip")
        self.assertInsensitiveEqual(url, "https://github.com/jdfreder/jupyter-pip")

    def test_widgetsnbextension(self):
        # https://github.com/jupyter-widgets/ipywidgets/tree/master/widgetsnbextension
        self.assertRaisesNoUrls("widgetsnbextension")

    def test_widgetsnbextension_old(self):
        self.assertRaisesNoUrls("jupyter-js-widgets-nbextension")

    def test_jupyterlab(self):
        url = self.converter.get_vcs("jupyterlab")
        self.assertInsensitiveEqual(url, "https://github.com/jupyterlab/jupyterlab")

    def test_jupyterlab_server(self):
        url = self.converter.get_vcs("jupyterlab-server")
        self.assertInsensitiveEqual(
            url, "https://github.com/jupyterlab/jupyterlab_server"
        )

    def test_jupyterlab_git(self):
        url = self.converter.get_vcs("jupyterlab-git")
        self.assertInsensitiveEqual(url, "https://github.com/jupyterlab/jupyterlab-git")

    def test_jupyterlab_latex(self):
        url = self.converter.get_vcs("jupyterlab-latex")
        self.assertInsensitiveEqual(
            url, "https://github.com/jupyterlab/jupyterlab-latex"
        )

    def test_jupyterlab_nvdashboard(self):
        url = self.converter.get_vcs("jupyterlab-nvdashboard")
        self.assertInsensitiveEqual(
            url, "https://github.com/rapidsai/jupyterlab-nvdashboard"
        )

    def test_jupyterlab_bokeh_server(self):
        url = self.converter.get_vcs("jupyterlab-bokeh-server")
        self.assertInsensitiveEqual(
            url, "https://github.com/ian-r-rose/jupyterlab-bokeh-server"
        )

    def test_databrickslabs_jupyterlab(self):
        url = self.converter.get_vcs("databrickslabs-jupyterlab")
        self.assertInsensitiveEqual(
            url, "https://github.com/databrickslabs/Jupyterlab-Integration"
        )

    def test_jupyterthemes(self):
        url = self.converter.get_vcs("jupyterthemes")
        self.assertInsensitiveEqual(url, "https://github.com/dunovank/jupyter-themes")

    def test_jupyter_contrib_nbextensions(self):
        url = self.converter.get_vcs("jupyter_contrib_nbextensions")
        self.assertInsensitiveEqual(
            url, "https://github.com/ipython-contrib/jupyter_contrib_nbextensions"
        )

    def test_jupyter_nbextensions_configurator(self):
        url = self.converter.get_vcs("jupyter_nbextensions_configurator")
        self.assertInsensitiveEqual(
            url, "https://github.com/jupyter-contrib/jupyter_nbextensions_configurator"
        )

    def test_jupyterlab_pygments(self):
        self.assertRaisesNoUrls("jupyterlab-pygments")

    def test_matplotlib(self):
        url = self.converter.get_vcs("matplotlib")
        self.assertInsensitiveEqual(url, "https://github.com/matplotlib/matplotlib")

    def test_ipympl(self):
        # https://github.com/matplotlib/jupyter-matplotlib
        self.assertRaisesNoUrls("ipympl")

    def test_cycler(self):
        url = self.converter.get_vcs("cycler")
        self.assertInsensitiveEqual(url, "https://github.com/matplotlib/cycler")

    def test_pyviz(self):
        url = self.converter.get_vcs("pyviz")
        self.assertInsensitiveEqual(url, "https://github.com/pyviz/pyviz")

    def test_pyviz_comms(self):
        url = self.converter.get_vcs("pyviz-comms")
        self.assertInsensitiveEqual(url, "https://github.com/holoviz/pyviz_comms")


class TestROS(_TestBase):
    def test_catkin(self):
        url = self.converter.get_vcs("catkin")
        self.assertInsensitiveEqual(url, "https://github.com/ros/catkin")

    def test_catkin_pkg(self):
        url = self.converter.get_vcs("catkin-pkg")
        self.assertInsensitiveEqual(
            url, "https://github.com/ros-infrastructure/catkin_pkg"
        )

    def test_rosdep(self):
        url = self.converter.get_vcs("rosdep")
        self.assertInsensitiveEqual(url, "https://github.com/ros-infrastructure/rosdep")

    def test_rosdistro(self):
        url = self.converter.get_vcs("rosdistro")
        self.assertInsensitiveEqual(url, "https://github.com/ros/rosdistro")

    def test_wstool(self):
        url = self.converter.get_vcs("wstool")
        self.assertInsensitiveEqual(url, "https://github.com/vcstools/wstool")

    def test_rosinstall(self):
        url = self.converter.get_vcs("rosinstall")
        self.assertInsensitiveEqual(url, "https://github.com/vcstools/rosinstall")

    def test_rosinstall_generator(self):
        url = self.converter.get_vcs("rosinstall_generator")
        self.assertInsensitiveEqual(
            url, "https://github.com/ros-infrastructure/rosinstall_generator"
        )


class TestOrange(_TestBase):
    def test_orange3(self):
        url = self.converter.get_vcs("orange3")
        self.assertInsensitiveEqual(url, "https://github.com/biolab/orange3")

    def test_orange(self):
        url = self.converter.get_vcs("orange")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/biolab/orange")

    def test_orange_widget_base(self):
        url = self.converter.get_vcs("orange-widget-base")
        self.assertInsensitiveEqual(url, "https://github.com/biolab/orange-widget-base")

    def test_orange_canvas_core(self):
        url = self.converter.get_vcs("orange_canvas-core")
        self.assertInsensitiveEqual(url, "https://github.com/biolab/orange-canvas-core")

    def test_orange3_ImageAnalytics(self):
        url = self.converter.get_vcs("orange3-ImageAnalytics")
        self.assertInsensitiveEqual(
            url, "https://github.com/biolab/orange3-ImageAnalytics"
        )

    def test_orange3_Recommendation(self):
        url = self.converter.get_vcs("orange3-Recommendation")
        self.assertInsensitiveEqual(
            url, "https://github.com/biolab/orange3-Recommendation"
        )

    def test_orange_text(self):
        url = self.converter.get_vcs("orange-Text")
        self.assertInsensitiveEqual(url, "https://bitbucket.org/biolab/orange-text")

    def test_orange3_text(self):
        url = self.converter.get_vcs("orange3-text")
        self.assertInsensitiveEqual(url, "https://github.com/biolab/orange3-text")

    def test_nonpypi_PyQtTester(self):
        with self.assertRaises(InvalidPackage):
            self.converter.get_vcs("PyQtTester")


class TestEnthought(_TestBase):
    def test_grin(self):
        url = self.converter.get_vcs("grin")
        self.assertInsensitiveEqual(url, "https://github.com/rkern/grin")

    def test_traits(self):
        url = self.converter.get_vcs("traits")
        self.assertInsensitiveEqual(url, "https://github.com/enthought/traits")

    def test_traitsui(self):
        url = self.converter.get_vcs("traitsui")
        self.assertInsensitiveEqual(url, "https://github.com/enthought/traitsui")

    def test_etsdevtools(self):
        url = self.converter.get_vcs("etsdevtools")
        self.assertInsensitiveEqual(url, "https://github.com/enthought/etsdevtools")


class TestGnome(_TestBase):
    def test_pygtk(self):
        url = self.converter.get_vcs("pygtk")
        self.assertInsensitiveEqual(url, "https://gitlab.gnome.org/gnome/pygobject")

    def test_pygobject(self):
        url = self.converter.get_vcs("pygobject")
        self.assertInsensitiveEqual(url, "https://gitlab.gnome.org/gnome/pygobject")

    def test_pyocr(self):
        url = self.converter.get_vcs("pyocr")
        self.assertEqual(url, "https://gitlab.gnome.org/World/OpenPaperwork/pyocr")

    def test_pyinsane2(self):
        url = self.converter.get_vcs("pyinsane2")
        self.assertInsensitiveEqual(url, "https://github.com/openpaperwork/pyinsane")
        # Should be "https://gitlab.gnome.org/World/OpenPaperwork/pyinsane")

    def test_pypillowfight(self):
        url = self.converter.get_vcs("pypillowfight")
        self.assertEqual(url, "https://gitlab.gnome.org/World/OpenPaperwork/libpillowfight")


class TestQt(_TestBase):
    def _test_dip(self):
        url = self.converter.get_vcs("dip")
        self.assertInsensitiveEqual(url, "https://www.riverbankcomputing.com/hg/dip")

    def test_pyqtdeploy(self):
        url = self.converter.get_vcs("pyqtdeploy")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/software/pyqtdeploy"
        )

    def _test_pyqt_builder(self):
        url = self.converter.get_vcs("PyQt-builder")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/hg/PyQt-builder"
        )

    def test_sip(self):
        url = self.converter.get_vcs("sip")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/software/sip"
        )

    def test_pyqt4(self):
        url = self.converter.get_vcs("pyqt4")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/software/pyqt"
        )

    def _test_pyqt4_sip(self):
        url = self.converter.get_vcs("pyqt4-sip")
        self.assertInsensitiveEqual(url, "https://sourceforge.net/projects/pyqt4")

    def test_pyqt5(self):
        # Maybe should be https://sourceforge.net/projects/pyqt5
        url = self.converter.get_vcs("pyqt5")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/software/pyqt"
        )

    def test_pyqt5_sip(self):
        url = self.converter.get_vcs("pyqt5-sip")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/software/sip"
        )

    def test_pyqtchart(self):
        url = self.converter.get_vcs("pyqtchart")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/software/pyqtchart"
        )

    def test_pyqtwebengine(self):
        url = self.converter.get_vcs("pyqtwebengine")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/software/pyqtwebengine"
        )

    def test_pyqtdatavisualization(self):
        url = self.converter.get_vcs("pyqtdatavisualization")
        self.assertInsensitiveEqual(
            url, "https://www.riverbankcomputing.com/software/pyqtdatavisualization"
        )


class TestFreedesktop(_TestBase):
    def test_pyxdg(self):
        # https://github.com/jayvdb/pypidb/issues/41 should be
        # http://cgit.freedesktop.org/xdg/pyxdg/
        url = self.converter.get_vcs("pyxdg")
        #self.assertInsensitiveEqual(url, "https://github.com/takluyver/pyxdg")
        self.assertInsensitiveEqual(url, "https://gitlab.freedesktop.org/xdg/pyxdg")

    def test_dbus(self):
        url = self.converter.get_vcs("dbus-python")
        self.assertInsensitiveEqual(url, "https://gitlab.freedesktop.org/dbus/dbus-python")

    def test_hid_tools(self):
        url = self.converter.get_vcs("hid-tools")
        self.assertInsensitiveEqual(url, "https://gitlab.freedesktop.org/libevdev/hid-tools")

    def test_libevdev(self):
        url = self.converter.get_vcs("libevdev")
        self.assertInsensitiveEqual(url, "https://gitlab.freedesktop.org/libevdev/python-libevdev")

    def test_xpyb(self):
        url = self.converter.get_vcs("xpyb")
        self.assertInsensitiveEqual(url, "https://gitlab.freedesktop.org/xcb/xpyb")


class TestMaxmind(_TestBase):
    def test_GeoIP(self):
        url = self.converter.get_vcs("GeoIP")
        self.assertInsensitiveEqual(url, "https://github.com/maxmind/GeoIP-api-python")

    def test_GeoIP2(self):
        url = self.converter.get_vcs("GeoIP2")
        self.assertInsensitiveEqual(url, "https://github.com/maxmind/GeoIP2-python")

    def test_minfraud(self):
        url = self.converter.get_vcs("minfraud")
        self.assertInsensitiveEqual(url, "https://github.com/maxmind/minfraud-api-python")
