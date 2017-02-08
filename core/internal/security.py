import cherrypy
SESSION_KEY = '_cp_username'
LOGIN_FORM = '/loginform'

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
    if username is None or password is None:
        return False
    cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
    return True

def do_logout():
    sess = cherrypy.session
    username = sess.get(SESSION_KEY, None)
    sess[SESSION_KEY] = None
    if username:
        cherrypy.request.login = None

#Adds dashboards.auth to the CherryPy config
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)
