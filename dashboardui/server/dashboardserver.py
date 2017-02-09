import os

import cherrypy

from dashboardui.dashboard import Dashboard, DashboardAction
from dashboardui.server.security import require, do_login, do_logout, ajax_call, set_login_form


class DashboardServer(object):
    """
    HTTP server for the dashboards. Only one instance of this class should be created.
    """
    def __init__(self, title, description, root_dashboard_group, authentication = None):
        Dashboard.app_setup(title, description, root_dashboard_group)

        dr = os.path.dirname(os.path.realpath(__file__))
        st_dir = os.path.join(dr, "static")

        main_cfg = {'tools.sessions.on': True, 'tools.auth.on': True}
        static_cfg = {"tools.staticdir.on" : True, "tools.staticdir.dir" : st_dir}
        dashboard_server_config = {'/' : main_cfg, "/static" : static_cfg }

        set_login_form('/' + self.loginform.__name__)

        self.main_dashboard = Dashboard("title", "description", "main_template.html")
        self.login_page = Dashboard("title", "description", "login.html")
        self.logged_out_page = Dashboard("title", "description", "loggedout.html")

        cherrypy.quickstart(self, '/', dashboard_server_config)

    @require()
    @cherrypy.expose
    def index(self):
        return self.main_dashboard.render()

    @cherrypy.expose
    def loginform(self):
        return self.login_page.render()

    @cherrypy.expose
    def loggedout(self):
        return self.logged_out_page.render()

    @cherrypy.expose
    def loginaction(self, username=None, password=None):
        if not do_login(username, password):
            raise cherrypy.HTTPRedirect("/loginform")
        raise cherrypy.HTTPRedirect("/")

    @require()
    @cherrypy.expose
    def logoutaction(self):
        do_logout()
        raise cherrypy.HTTPRedirect("/loggedout")

    @require()
    @cherrypy.expose
    @ajax_call
    def dashboard_action(self, action_class, action_params, **kwargs):
        return DashboardAction.from_url_path_no_unquote(action_class, action_params, **kwargs).execute().render()

    @require()
    @cherrypy.expose
    @ajax_call
    def dashboard(self, dashboard_id):
        return Dashboard.getDashboardById(dashboard_id).render()


