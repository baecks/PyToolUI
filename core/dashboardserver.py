import cherrypy
import os
from jinja2 import Environment, FileSystemLoader
from internal.security import require, do_login, do_logout
from dashboards.dashboards import Dashboard

class DashboardServerData(object):
    def __init__(self):
        pass

    @property
    def username(self):
        return cherrypy.request.login

class DashboardServer(object):
    def __init__(self, title, dashboards, authentication = None):
        dr = os.path.dirname(os.path.realpath(__file__))
        st_dir = os.path.join(dr, "static")

        self.dashboards = dashboards

        #JINJA2 environment for template loading
        self.env = Environment(loader=FileSystemLoader(os.path.join(dr, "templates")))

        #JINJA2 template data
        self.tmlp_data = {'title' : title, 'dashboards' : self.dashboards, 'data' : DashboardServerData()}

        main_cfg = {'tools.sessions.on': True, 'tools.auth.on': True}
        static_cfg = {"tools.staticdir.on" : True, "tools.staticdir.dir" : st_dir}
        dashboard_server_config = {'/' : main_cfg, "/static" : static_cfg }

        cherrypy.loginform = "/loginform"

        cherrypy.quickstart(self, '/', dashboard_server_config)


    @require()
    @cherrypy.expose
    def index(self):
        return self.processTemplate("main_template.html")

    @cherrypy.expose
    def loginform(self):
        return self.processTemplate("login.html")

    @cherrypy.expose
    def loggedout(self):
        return self.processTemplate("loggedout.html")

    @cherrypy.expose
    def loginaction(self, username=None, password=None):
        if not do_login(username, password):
            raise cherrypy.HTTPRedirect("/loginform")
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def logoutaction(self):
        do_logout()
        raise cherrypy.HTTPRedirect("/loggedout")

    def processTemplate(self, tmpl, additional_data=None):
        try:
            template = self.env.get_template(os.path.basename(tmpl))
            data = self.tmlp_data
            if (additional_data != None):
                data.update(additional_data)
            return template.render(data)
        except Exception as e:
            print ("Error: Failed to load the template file (%s)!\n" % str(e))
            raise Exception("ERROR rendering page: %s" % str(e))

    # def _dashboard_processing(self, dashboardname, reset, **kwargs):
    #     dashboard = DashboardGroup.findDashboardByName(dashboardname)
    #     if dashboard == None:
    #         raise ("Invalid dashboard: %s" % dashboardname)
    #
    #     render_data = {'dashboard' : dashboard}
    #
    #     if reset == True:
    #         try:
    #             dashboard.reset()
    #         except Exception as e:
    #             render_data['error'] = "Reset failed (%s)" % str(e)
    #     else:
    #         if cherrypy.request.method.lower() == 'post':
    #             try:
    #                 dashboard.setParameters(kwargs)
    #             except Exception as e:
    #                 render_data['error'] = "Failed to set the parameter values (%s)" % str(e)
    #             try:
    #                 dashboard.validate()
    #             except Exception as e:
    #                 render_data['error'] = "Validation failed (%s)" % str(e)
    #
    #             try:
    #                 dashboard.commit()
    #             except Exception:
    #                 render_data['error'] = "Commit failed (%s)" % str(e)
    #
    #         return self.processTemplate(dashboard.getTemplate(), render_data)


    @cherrypy.expose()
    def dashboard(self, dashboardname, **kwargs):
        tmpl, data = Dashboard.load_from_request_data(cherrypy.request, dashboardname, **kwargs)
        return self.processTemplate(tmpl, data)


