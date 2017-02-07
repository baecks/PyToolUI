import importlib
import inspect
import os
import threading
import cherrypy
from jinja2 import Environment, FileSystemLoader
from dashboards.propertyproxy import BaseProxy, PropertyProxy
from dashboards.helpers import get_class_from_name
import json
import urllib

PROPERTY_PARAM_PREFIX = "PROP_REF_ID___"
SUBMIT_PARAM_PREFIX = "SUBMIT_PROP_ID___"
DASHBOARD_INSTANCE_PREFIX = "DASHBOARD___"

URL_PARAMETER_PROP_REF_PREFIX = "PROP___"

PROXIED_PREFIX = "PROXIED___"

class DashboardGroup(object):
    def __init__(self, title):
        self.title = title
        self._dashboards_and_groups = []
        self.group = True

    def add(self, dashboard):
        if dashboard == None:
            raise Exception("No dashboard or group provided!")

        if not isinstance(dashboard, Dashboard) and not isinstance(dashboard, DashboardGroup):
            raise Exception("No valid dashboard or group provided!")

        self._dashboards_and_groups.append(dashboard)

    def get_all(self):
        return self._dashboards_and_groups


class DashboardServerData(object):
    def __init__(self, app_title, dashboards):
        if app_title == None:
            raise Exception("No application tile provided!")

        if len(app_title) < 5:
            raise Exception("An application title needs to be at least 5 characters!")

        self._app_title = app_title

        if dashboards == None:
            raise Exception("No dashboard structure provided!")

        if not isinstance(dashboards, DashboardGroup):
            raise Exception(
                "The dashboard structure object provided is not an instance of %s!" % DashboardGroup.__name__)

        self._app_dashboards = dashboards.get_all()

    def _get_logged_in_user(self):
        try:
            return cherrypy.request.login
        except:
            return "None"

    user = property(fget=_get_logged_in_user)
    name = property(fget=lambda self: self._app_title)
    dashboards = property(fget=lambda self: self._app_dashboards)


# class DashboardAction(object):
#     _REF_ID_SUFFIX = "___PROPERTY_REF"
#
#     @staticmethod
#     def _class_object(action_class):
#         parts = action_class.split('.')
#         module_name = ".".join(parts[:-1])
#         mod = importlib.import_module(module_name)
#         cls = getattr(mod, parts[-1])
#         if issubclass(cls, DashboardAction) and cls != DashboardAction:
#             return cls
#         raise("Class %s is not a sub-class of %s" % (action_class, DashboardAction.__name__))
#
#     @staticmethod
#     def _instance_from_name(action_class_name, **kwargs):
#         cls = DashboardAction._class_object(action_class_name)
#         args = list(kwargs.keys())
#         args.sort()
#         parameter_list = []
#         for arg in args:
#             if arg.endswith(DashboardAction._REF_ID_SUFFIX):
#                 # It is a proxied value
#                 try:
#                     parameter = BaseProxy.getPropertyById(kwargs[arg])
#                 except:
#                     raise("Non existing proxied parameter specified (%s)!" % arg)
#                 parameter_list.append(parameter)
#             else:
#                 parameter_list.a
#
#     def from_url
#     def __init__(self, *args):
#         for arg in args:
#             if not isinstance(arg, BaseProxy):
#                 raise("Arguments should be instances of %s" % BaseProxy.__name__)
#
#         self._process_args(args)
#
#     def _process_args(self, args):
#
#
#     def _get_js_action(self):
#         return ""

class DashboardAction(object):
    def __init__(self, *args, **kwargs):
        pass

    def execute(self):
        return Dashboard("Generic action", "Generic action", None)

    def get_url(self):
        return ""


class Dashboard(object):
    _id2obj_lock = threading.RLock()
    _id2obj_global_dict = {}

    @staticmethod
    def _remember(obj):
        oid = str(id(obj))
        Dashboard._id2obj_lock.acquire()
        Dashboard._id2obj_global_dict[oid] = obj
        Dashboard._id2obj_lock.release()
        return oid

    @staticmethod
    def _id2obj(oid):
        Dashboard._id2obj_lock.acquire()
        obj = Dashboard._id2obj_global_dict[oid]
        Dashboard._id2obj_lock.release()
        return obj

    @staticmethod
    def getDashboardById(oid):
        return Dashboard._id2obj(oid)

    @staticmethod
    def _class_object(dashboard_class):
        parts = dashboard_class.split('.')
        module_name = ".".join(parts[:-1])
        mod = importlib.import_module(module_name)
        cls = getattr(mod, parts[-1])
        if issubclass(cls, Dashboard) and cls != Dashboard:
            return cls
        raise Exception("Class %s is not a sub-class of %s" % (dashboard_class, Dashboard.__name__))

    @staticmethod
    def _instance_from_name(dashboard_class_name, title=None, **kwargs):
        cls = Dashboard._class_object(dashboard_class_name)
        return cls(title, kwargs)

    @staticmethod
    def _instance_from_class(dashboard_class, title=None, **kwargs):
        return dashboard_class(title, kwargs)

    @staticmethod
    def request_to_python(request, dashboard_name, **kwargs):
        global PROPERTY_PARAM_PREFIX, SUBMIT_PARAM_PREFIX

        # Check if the dashboard being requested exists
        try:
            dashboard_cls = Dashboard._class_object(dashboard_name)
        except:
            raise ("The dashboard %s does not exist!" % dashboard_name)

        # Get the __init__ signature
        try:
            dashboard_init_sig = inspect.getargfullspec(dashboard_cls.__init__)
        except:
            raise Exception("Failed to get the initialization signature for dashboard %s!" % dashboard_cls.__name__)

        # An __init__ function can take several types of parameters, in the order listed below:
        # - positional arguments
        # - positional arguments having a default value
        # - variable positional (unnamed) arguments (*args)
        # - keyword arguments
        # - keyword arguments having a default value
        # - variable keyword unnamed arguments (**kwargs)

        # Positional arguments
        dashboard_init_positional_arguments = {}
        dashboard_init_positional_arguments_defaults = [None] * (
        len(dashboard_init_sig.args) - len(dashboard_init_sig.defaults or [])) + dashboard_init_sig.defaults
        for i in len(dashboard_init_sig.args):
            arg = dashboard_init_sig.args[i]
            dashboard_init_positional_arguments[arg] = dashboard_init_positional_arguments_defaults[i]

        # variable positional arguments
        dashboard_init_has_varargs = (dashboard_init_sig.varargs != None)

        # Keyword arguments
        dashboard_init_keyword_arguments = {}
        # dashboard_init_keyword_arguments_defaults = [None]*(len(dashboard_init_sig.kwonlyargs)-len(dashboard_init_sig.defaults)) + dashboard_init_sig.defaults
        for arg in dashboard_init_sig.kwonlyargs:
            dashboard_init_keyword_arguments[arg] = None
            dashboard_init_positional_arguments[arg] = dashboard_init_positional_arguments_defaults[i]

        # Process the arguments sent over from the client
        # Proxied data is referenced by their ID. The parameters specifying proxied properties have a name starting
        # with PROPERTY_PARAM_PREFIX.
        prop_params = [x for x in kwargs.keys() if x.startswith(PROPERTY_PARAM_PREFIX)]
        instance_parameters = {}
        for prop in prop_params:
            prop_name = prop[len(PROPERTY_PARAM_PREFIX):]
            try:
                value = BaseProxy.getPropertyById(kwargs[prop])
            except:
                raise Exception("Invalid property reference (%s)!" % prop_name)
            instance_parameters[prop_name] = value

        # Process the values to set (=submitted to the back-office data that is proxied)
        # Proxied data is referenced by their ID. The parameters to be set have to be properties (PropertyProxy)
        # and  ave a name starting with SUBMIT_PARAM_PREFIX.
        submit_properties = [x for x in kwargs.keys() if x.startswith(SUBMIT_PARAM_PREFIX)]
        submit_values = {}
        for prop in submit_properties:
            prop_id = prop[len(SUBMIT_PARAM_PREFIX):]
            try:
                prop_obj = BaseProxy.getPropertyById(prop_id)
            except:
                raise Exception("Invalid property reference (%s)!" % prop)

            if not isinstance(prop_obj, PropertyProxy):
                raise Exception("The reference is not a property (%s)!" % prop)

            submit_values[prop_obj] = kwargs[prop]

        # Create the dashboard instance and pass all data
        dashboard = Dashboard._instance_from_class(dashboard_name, )

    @staticmethod
    def load_from_request_data(request, dashboard_name, **kwargs):
        global PROPERTY_PARAM_PREFIX, VALUE_PARAM_PREFIX, DASHBOARD_INSTANCE_PREFIX
        PROPERTY_PARAM_SUFFIX = "___ID"
        # Check if the dashboard being requested is an instance or a new one to be created
        if dashboard_name.startswith(DASHBOARD_INSTANCE_PREFIX):
            try:
                dashboard_id = dashboard_name[len(DASHBOARD_INSTANCE_PREFIX):]
                dashboard_instance = Dashboard.getDashboardById(dashboard_id)
            except:
                raise Exception("Failed to obtain the dashboard instance %s!" % dashboard_name)

            return dashboard_instance.get_render_data()

        # Process the arguments sent over from the client
        prop_params = [x for x in kwargs.keys() if x.startswith(PROPERTY_PARAM_SUFFIX)]
        instance_parameters = {}
        for prop in prop_params:
            prop_name = prop[:-len(PROPERTY_PARAM_SUFFIX)]
            try:
                value = BaseProxy.getPropertyById(kwargs[prop])
            except:
                raise Exception("Invalid property reference (%s)!" % prop_name)
            instance_parameters[prop_name] = value

        # Create a dashboard instance using the dashboard properties
        try:
            dashboard = Dashboard._instance(dashboard_name, **instance_parameters)
        except Exception as e:
            raise Exception("Dashboard \"%s\" creation failed dashboard (%s)!" % (dashboard_name, str(e)))

        # Set property values bases on the remaining parameters
        request_parameters = [x for x in kwargs.keys() if x.startswith(VALUE_PARAM_PREFIX)]
        for prop_name in request_parameters:
            try:
                prop = BaseProxy.getPropertyById(prop_name[len(VALUE_PARAM_PREFIX):])
            except:
                raise Exception("Referenced invalid property (%s)!" % prop_name)

            prop.set_commit_value_from_string(kwargs[prop_name])

        if request.method.lower() == 'post':
            # Process the data that got submitted
            dashboard.error_msg = dashboard.validate()
            if dashboard.error_msg == None:
                dashboard.commit()

        # Render the dashboard
        return dashboard.get_render_data()

    @staticmethod
    def app_setup(app_title, dashboards):
        dr = os.path.dirname(os.path.realpath(__file__))

        # JINJA2 environment for template loading
        Dashboard._env = Environment(loader=FileSystemLoader(os.path.join(dr, "templates")))

        # JINJA2 template data
        Dashboard._app_template_data = {'app_data': DashboardServerData(app_title, dashboards),
                                        "dashboard_action" : DashboardAction.dashboard_action,
                                        "dashboard_action_url" : DashboardAction.dashboard_action_url}

    def __init__(self, title, description, template, **kwargs):
        """

        Args:
            title:
            properties:
        """

        self.uid = Dashboard._remember(self)
        self.error_msg = None
        self.commit_only_if_different = True
        self.title = title or "Generic dashboard"
        self.template = template or "generic_dashboard.html"
        self.properties = {}
        self.description = description
        for prop_name, prop in kwargs.items():
            if not isinstance(prop, BaseProxy):
                continue
            self.properties[prop_name] = prop

        self._template_variables_to_be_exposed = []

    def get_additional_render_data(self):
        return {}

    def validate(self):
        """

        Returns:
            The function should return None (= success) or a text string identifying the problem
        """
        return None

    def reset(self):
        for m in self.properties:
            m.reset()

    def commit(self):
        for m in self.properties:
            m.commit(self.commit_only_if_different)

    def get_template(self):
        return self.template

    def render(self):
        try:
            template = Dashboard._env.get_template(self.get_template())
            data = self.get_additional_render_data()
            data.update(Dashboard._app_template_data)
            data.update(self.properties)
            data['title'] = self.title
            data['description'] = self.description
            return template.render(data)
        except Exception as e:
            raise Exception("ERROR rendering page: %s" % str(e))


class DashboardAction(object):
    def __init__(self, *args, **kwargs):
        self._init_args = args
        self._init_kwargs = kwargs

        self._properties_commited = []

    @staticmethod
    def _get_dashboard_action_object(action_cls, *args, **kwargs):
        try:
            cls = get_class_from_name(action_cls)
            return cls(*args, **kwargs)
        except Exception as e:
            raise Exception("Failed to create action (%s)!" % str(e))

    @staticmethod
    def dashboard_action(action_cls, *args, **kwargs):
        return DashboardAction._get_dashboard_action_object(action_cls, *args, **kwargs).js

    @staticmethod
    def dashboard_action_url(action_cls, *args, **kwargs):
        return DashboardAction._get_dashboard_action_object(action_cls, *args, **kwargs).url

    @staticmethod
    def _encode_proxy(v):
        if v == None:
            return v
        if isinstance(v, BaseProxy):
            return PROXIED_PREFIX + v.uid
        return v

    @staticmethod
    def _decode_proxy(v):
        if v == None:
            return v

        if not isinstance(v, str):
            return v

        if not v.startswith(PROXIED_PREFIX):
            return v

        return DashboardAction._get_property_by_url_id(v)

    @staticmethod
    def _get_property_by_url_id(id):
        return BaseProxy.getPropertyById(id[len(PROXIED_PREFIX):])

    def get_url(self):
        positional_args = []
        for arg in self._init_args:
            positional_args.append(DashboardAction._encode_proxy(arg))

        named_args = {}
        for n, arg in self._init_kwargs.items():
            named_args[n] = DashboardAction._encode_proxy(arg)

        url_path = "dashboard_action/" + self.__module__ + "." + self.__class__.__name__ + "/"
        try:
            parameters = json.dumps({'args': positional_args, 'kwargs' : named_args })
            url_path += urllib.parse.quote(parameters)
        except Exception as e:
            raise Exception("Failed to create the parameter URL path (%s)!" % str(e))
        return url_path

    def get_javascript(self):
        return "action('%s');" % self.url


    @staticmethod
    def from_url_path(class_name, parameters, **kwargs):
        params = urllib.parse.unquote(parameters)
        return DashboardAction.from_url_path_no_unquote(class_name, params, **kwargs)

    @staticmethod
    def from_url_path_no_unquote(class_name, parameters, **kwargs):
        cls = get_class_from_name(class_name)

        if not issubclass(cls, DashboardAction):
            raise Exception("Class %s is not a sub-class of %s" % (class_name, DashboardAction.__name__))

        # Parse the parameters
        try:
            args = json.loads(parameters)
        except Exception as e:
            raise Exception("Failed to parse the parameters (%s)!" % str(e))

        # Get the postional parameters
        try:
            postional_args = [DashboardAction._decode_proxy(x) for x in args['args']]
        except:
            raise Exception("Failed to get the positional arguments!")

        # Get keyword arguments
        try:
            named_args = {}
            named_args_encoded = args['kwargs']
            for k, v in named_args_encoded.items():
                named_args[k] = DashboardAction._decode_proxy(v)
        except:
            raise Exception("Failed to get the positional arguments!")

        # Set the proxied properties passed as **kwargs
        properties_commited = []
        for n, v in kwargs.items():
            try:
                proxy_object = BaseProxy.getPropertyById(n)
                proxy_object.value = v
                properties_commited.append(v)
            except:
                raise Exception("Failed to find proxied property \"%s\" and set the value (%s)!" % (str(n), v))

        try:
            o = cls(*postional_args, **named_args)
            o.set_properties_committed(properties_commited)
        except Exception as e:
            raise Exception("Failed to instantiate the action (%s)!" % str(e))

        return o

    def set_properties_committed(self, props):
        if props == None:
            return

        if not isinstance(props, list):
            raise Exception ("The properties should be provided as a list!")

        for p in props:
            if not isinstance(p, PropertyProxy):
                raise Exception("The list contains a non-%s instance (%s)!" % (PropertyProxy.__name__, str(p)) )

        self._properties_commited = props

    def commit_properties(self):
        for v in self._properties_commited:
            v.commit()

    def reset_properties(self):
        for v in self._properties_commited:
            v.reset()

    @staticmethod
    def test_url_path(url):
        parts = url.split("/")
        o = DashboardAction.from_url_path(parts[1], parts[2])
        return o

    def execute(self):
        self.commit_properties()
        return Dashboard("x", "x", None)

    url = property(fget=get_url)
    js = property(fget=get_javascript)
