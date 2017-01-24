import cherrypy
import os
from jinja2 import Environment, FileSystemLoader
from internal.security import require, do_login, do_logout
from ..tools.tools import ToolGroup

class ToolServerData(object):
    def __init__(self):
        pass

    @property
    def username(self):
        return cherrypy.request.login

class ToolServer(object):
    def __init__(self, title, authentication = None):
        dr = os.path.dirname(os.path.realpath(__file__))
        st_dir = os.path.join(dr, "static")

        #JINJA2 environment for template loading
        self.env = Environment(loader=FileSystemLoader(os.path.join(dr, "templates")))

        #JINJA2 template data
        self.tmlp_data = {'title' : title, 'tools' : ToolGroup.tools_and_groups, 'data' : ToolServerData() }

        main_cfg = {'tools.sessions.on': True, 'tools.auth.on': True}
        static_cfg = {"tools.staticdir.on" : True, "tools.staticdir.dir" : st_dir}
        tool_server_config = {'/' : main_cfg, "/static" : static_cfg }

        #cherrypy.loginform = "/loginform"

        cherrypy.quickstart(self, '/', tool_server_config)

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

    def processTemplate(self, tmpl):
        try:
            template = self.env.get_template(os.path.basename(tmpl))
            return template.render(self.tmlp_data)
        except Exception as e:
            print ("Error: Failed to load the template file (%s)!\n" % str(e))
            return "ERROR: %s" % str(e)

    def tool(self, toolname):
        pass
    

