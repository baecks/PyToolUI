from .propertyproxy import BaseProxy
import importlib
import threading

PROPERTY_PARAM_SUFFIX = "___REF_ID"
VALUE_PARAM_PREFIX = "PROP___"
DASHBOARD_INSTANCE_PREFIX = "DASHBOARD___"

class DashboardBase(object):
    _id2obj_lock = threading.RLock()
    _id2obj_global_dict = {}

    @staticmethod
    def _remember(obj):
        oid = id(obj)
        DashboardBase._id2obj_lock.acquire()
        DashboardBase._id2obj_global_dict[oid] = obj
        DashboardBase._id2obj_lock.release()
        return oid

    @staticmethod
    def _id2obj(oid):
        DashboardBase._id2obj_lock.acquire()
        obj = DashboardBase._id2obj_global_dict[int(oid)]
        DashboardBase._id2obj_lock.release()
        return obj

    @staticmethod
    def getDashboardById(oid):
        return DashboardBase._id2obj(oid)

    @staticmethod
    def _instance(dashboard_class, title=None, **kwargs):
        parts = dashboard_class.split('.')
        module_name = ".".join(parts[:-1])
        mod = importlib.import_module(module_name)
        cls = getattr(mod, parts[-1])
        return cls(title, kwargs)

    @staticmethod
    def load_from_request_data(request, dashboard_name, **kwargs):
        global PROPERTY_PARAM_SUFFIX, VALUE_PARAM_PREFIX, DASHBOARD_INSTANCE_PREFIX
        # Check if the dashboard being requested is an instance or a new one to be created
        if dashboard_name.startswith(DASHBOARD_INSTANCE_PREFIX):
            try:
                dashboard_id = dashboard_name[len(DASHBOARD_INSTANCE_PREFIX):]
                dashboard_instance = DashboardBase.getDashboardById(dashboard_id)
            except:
                raise Exception("Failed to obtain the dashboard instance %s!" % dashboard_name)

            return dashboard_instance.get_render_data()

        # Process the arguments sent over from the client
        prop_params = [x for x in kwargs.keys() if x.endswith(PROPERTY_PARAM_SUFFIX)]
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
            dashboard = DashboardBase._instance(dashboard_name, **instance_parameters)
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

    def __init__(self, title=None, template=None, **kwargs):
        """

        Args:
            title:
            properties:
        """

        self.uid = DashboardBase._remember(self)
        self.error_msg = None
        self.commit_only_if_different = True
        self.title = title or "Generic dashboard"
        self.template = template or "generic_dashboard.html"
        self.properties = {}
        for prop_name, prop in kwargs.iteritems():
            if not isinstance(prop, BaseProxy):
                continue

            self.properties[prop_name]=prop

    def get_render_data(self):
        data = {'dashboard' : self}
        data.update(self.properties)
        return self.template, data

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

    def getTemplate(self):
        return self.template
