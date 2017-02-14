import os
import cherrypy
from dashboardui.dashboard import Dashboard, DashboardAction

SESSION_KEY = '_cp_username'
LOGIN_ERROR = '__login_error_message'
LOGIN_FORM = '/loginform'
AUTHENTICATOR = None

def is_authentication_active():
    global AUTHENTICATOR
    return (AUTHENTICATOR != None)

def set_authenticator(auth):
    global AUTHENTICATOR
    if auth == None:
        AUTHENTICATOR = None
        return

    if not isinstance(auth, DashboardServerAuthenticator):
        raise Exception("The authenticator is not a sub-class of %s!" % DashboardServerAuthenticator.__name__)

    AUTHENTICATOR = auth

def set_login_form(form):
    global LOGIN_FORM
    if form == None:
        raise Exception("No login form provided!")

    if not isinstance(form, str):
        raise Exception("The login form should be a string!")

    LOGIN_FORM = form

def raise_authentication_failure():
    ajax = cherrypy.request.config.get('auth.ajax', False)
    if ajax:
        raise cherrypy.HTTPError(403, "FORBIDDEN")
    global LOGIN_FORM
    raise cherrypy.HTTPRedirect(LOGIN_FORM)

def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""

#    global LOGIN_FORM
#    try:
#        loginform = cherrypy.loginform
#    except:
#        loginform = LOGIN_FORM

    if not is_authentication_active():
        return

    conditions = cherrypy.request.config.get('auth.require', None)

    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise_authentication_failure()
        else:
            raise_authentication_failure()

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable.

    A condition is a function (optionally with parameters) that returns None in case of success. If a
    problem is detected the function should return any other value.

    Example:
        def check_credentials(username, password):
            if (username != None):
                return None
            return "Failure"
    """
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

def ajax_call(f):
    """A decorator identifies this method as an AJAX call. As a result no redirect to the login page
    will be sent upon authentication failure, but a 403 forbidden error.
    """
    if not hasattr(f, '_cp_config'):
        f._cp_config = dict()
    f._cp_config['auth.ajax'] = True
    return f

def do_login(username=None, password=None):
    if not is_authentication_active():
        return True

    if username is None or password is None:
        cherrypy.session[LOGIN_ERROR] = "Please provide a username and password!"
        return False

    global AUTHENTICATOR

    try:
        retval = AUTHENTICATOR.authenticate(username, password)
    except:
        cherrypy.session[LOGIN_ERROR] = "Could not execute authentication!"
        raise Exception("Authentication exception!")

    if not isinstance(retval, bool):

        cherrypy.session[LOGIN_ERROR] = "Authentication returned an invalid status!"
        raise Exception("Authentication returned an invalid status!")

    if retval:
        cherrypy.session[LOGIN_ERROR] = None
        cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
        return True

    cherrypy.session[LOGIN_ERROR] = "Username and/or password are invalid!"
    return False

def do_logout():
    if not is_authentication_active():
        return

    sess = cherrypy.session
    username = sess.get(SESSION_KEY, None)
    sess[SESSION_KEY] = None
    if username:
        cherrypy.request.login = None

#Adds dashboards.auth to the CherryPy config
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)


class DashboardServerAuthenticator(object):
    def __init__(self):
        pass

    def authenticate(self, user, password):
        return True

class CsvDashboardServerAuthenticator(DashboardServerAuthenticator):
    def __init__(self, csv):
        super(DashboardServerAuthenticator, self).__init__()

        if csv == None:
            raise Exception("No CSV file provided!")

        if not isinstance(csv, str):
            raise Exception("The CSV provided is not a string!")

        if not os.path.isfile(csv):
            raise Exception("The CSV is not a valid file!")

        f = open(csv)
        lns = f.readlines()
        f.close()

        self.users = {}

        for l in lns:
            cmps = l.strip().split(",")
            if len(cmps) != 2:
                raise Exception("Invalid line in the CSV file!")
            self.users[cmps[0].lower()]=cmps[1]


    def authenticate(self, user, password):
        try:
            pwd = self.users[user.lower()]
        except:
            return False

        return (pwd == password)

class LoginDashboard(Dashboard):
    def __init__(self):
        super(LoginDashboard, self).__init__("title", "description", "login.html")

    def get_additional_render_data(self):
        data = {}
        try:
            if cherrypy.session[LOGIN_ERROR] != None:
                data['msg'] = cherrypy.session[LOGIN_ERROR]
        except:
            data['msg'] = None

        return data


class DashboardServer(object):
    """
    HTTP server_static_files for the dashboards. Only one instance of this class should be created.
    """
    def __init__(self, title, description, root_dashboard_group, authenticator = None):
        Dashboard.app_setup(title, description, root_dashboard_group, (authenticator != None))

        set_authenticator(authenticator)

        dr = os.path.dirname(os.path.realpath(__file__))
        st_dir = os.path.join(dr, "server_static_files")

        main_cfg = {'tools.sessions.on': True, 'tools.auth.on': True}
        static_cfg = {"tools.staticdir.on" : True, "tools.staticdir.dir" : st_dir}
        dashboard_server_config = {'/' : main_cfg, "/static" : static_cfg }

        set_login_form('/' + self.loginform.__name__)

        self.main_dashboard = Dashboard("title", "description", "main_template.html")
        self.login_page = LoginDashboard()
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


