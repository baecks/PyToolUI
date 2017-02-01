from .internal.propertymappingbase import DashboardPropertyBase
import inspect
import cherrypy

SESSION_COMMIT_PREFIX="COMMIT_VALUE__"

class ScalarDashboardProperty(DashboardPropertyBase):
    def __init__(self, property_name, label, description, to_string, from_string, obj=None, getter=None, setter=None, read_only=True):
        super(ScalarDashboardProperty, self).__init__(property_name, label, description, obj)

        if (label == None) or (len(label) < 1):
            raise("Invalid label!")

        self.getter = getter
        self.setter = setter
        self.read_only = read_only

        if (self.setter != None) and (self.getter == None):
            raise Exception("A setter was provided, but no getter for property %s!" % self.property_name)

        if (self.read_only == False) and (self.getter != None) and (self.setter == None):
            raise Exception("Missing setter function for property %s!" % property_name)

        self.to_string = to_string
        self.from_string = from_string

        if (self.to_string == None):
            raise Exception ("No to_string converter!")
        if not inspect.isfunction(self.to_string):
            raise Exception ("Method to_string \"%s\" is not a function!" % self.to_string)

        if (self.from_string == None):
            raise Exception ("No from_string converter!")
        if not inspect.isfunction(self.from_string):
            raise Exception ("Method from_string \"%s\" is not a function!" % self.from_string)

        if self.is_bound():
            self.set_commit_value(None)

    def get_commit_value(self):
        self.check_bound()
        global SESSION_COMMIT_PREFIX
        try:
            val = cherrypy.session[SESSION_COMMIT_PREFIX + str(self.oid)]
        except:
            return self.get_value()

    def get_commit_value_as_string(self):
        self.check_bound()
        return self.to_string(self.get_commit_value())

    def set_commit_value(self, val):
        self.check_bound()
        global SESSION_COMMIT_PREFIX
        cherrypy.session[SESSION_COMMIT_PREFIX + str(self.oid)]=val

    def set_commit_value_from_string(self, str_val):
        self.check_bound()
        val = self.from_string(str_val)
        self.set_commit_value(val)

    def commit(self, if_different=True):
        if if_different:
            if (self.get_value() == self.get_commit_value()):
                return
        self.set_value(self.get_commit_value())
        self.reset()

    def reset(self):
        self.commit_value = None

    def get_value(self):
        self.check_bound()
        if self.getter == None:
            return getattr(self.bound_object, self.property_name)
        mt = getattr(self.bound_object, self.getter)
        return mt()

    def get_value_as_string(self):
        self.check_bound()
        return self.to_string(self.get_value())

    def set_value(self, val):
        self.check_bound()
        if self.is_read_only():
            raise("Property is read-only!")

        if self.setter == None:
            setattr(self.bound_object, self.property_name, val)
        else:
            mt = getattr(self.bound_object, self.setter)
            mt(val)

    def set_value_from_string(self, strval):
        self.check_bound()
        val = self.from_string(strval)
        self.set_value(val)

    def is_read_only(self):
        return self.read_only

class DashboardPropertiesHolder(object):
    """ Just a dummy class to hold the properies of an object
    """
    def __init__(self):
        super(DashboardPropertiesHolder, self).__init__()

class DashboardObject(DashboardPropertyBase):
    def __init__(self, property_name, unbound_prop_mappers, label = None, description = None, obj = None):
        super(DashboardObject, self).__init__(property_name, label, description, obj)
        self.properties = DashboardPropertiesHolder()

        for upm in unbound_prop_mappers:
            if (not isinstance(upm, DashboardPropertyBase)) or (upm.is_bound()):
                raise Exception("No unbound dashboard property (%s)" % str(upm))
            if self.is_bound():
                setattr(self.properties, upm.property_name, upm.bind(self.bound_object))
            else:
                setattr(self.properties, upm.property_name, upm)

    def bind(self, o):
        bound_obj = super(DashboardObject, self).bind(o)
        bound_props = []
        props = [getattr(bound_obj.properties, x) for x in dir(bound_obj.properties) if not x.startswith("__")]
        for prop in props:
            bound_props.append(prop.bind(o))
        bound_obj.properties = bound_props
        return bound_obj


class DashboardList(DashboardPropertyBase):
    def __init__(self, property_name, object_mapper, label = None, description = None, lst = None):
        super(DashboardList, self).__init__(property_name, label, description, lst)
        self.elems = []
        for elem in lst:
            wrapped_elem = object_mapper.bind(elem)
            self.elems.append(wrapped_elem)

# Property mapping for strings
prop_string_to_string = lambda x : x

class DashboardString(ScalarDashboardProperty):
    def __init__(self, property_name, label, description, obj = None, getter=None, setter=None, read_only=True):
        super(DashboardString, self).__init__(property_name, label, description, prop_string_to_string, prop_string_to_string,
                                                     obj, getter, setter, read_only)

# Property mapping for integers
prop_int_to_string = lambda x : str(x)
prop_string_to_int = lambda x : int(x)

class DashboardInt(ScalarDashboardProperty):
    def __init__(self, property_name, label, description, obj=None, getter=None, setter=None, read_only=True):
        super(DashboardInt, self).__init__(property_name, label, description, prop_int_to_string, prop_string_to_int,
                                                  obj, getter, setter, read_only)

# Fixed value string
class DashboardStringConstantHolder(object):
    """ Holds a string property for convenient wrapping
    """
    def __init__(self, str_val):
        self.str_val = str_val

class DashboardStringConstant(ScalarDashboardProperty):
    def __init__(self, str_value):
        super(DashboardStringConstant, self).__init__("str_val", str_value, prop_string_to_string,
                                                      prop_string_to_string, DashboardStringConstantHolder(str_value))
