import inspect

class DashboardPropertyMapperBase(object):
    def __init__(self, name, description, to_string, from_string, obj=None, prop=None, getter=None, setter=None, read_only=True):
        self.name = name
        if (self.name == None) or (len(self.name) < 1):
            raise Exception("Invalid property name!")

        self.obj = obj

        self.description = description
        if (self.description == None) or (len(self.description) < 5):
            raise Exception("Invalid property description!")

        self.getter = getter
        self.setter = setter
        self.prop = prop

        if (self.prop != None):
            self.getter = None
            self.setter = None
            self.read_only = read_only
        else:
            if (self.getter == None):
                raise Exception("If no property is specified, at least a getter method is required!")
            self.read_only = (self.setter == None)

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

        self.commit_values={}

    def get_commit_value(self, obj = None):
        o = self.obj or obj

        try:
            return self.commit_values[o]
        except:
            return self.get_value(o)

    def get_commit_value_as_string(self, obj = None):
        o = self.obj or obj

        val = self.get_commit_value(o)
        return self.to_string(val)

    def set_commit_value(self, val, obj = None):
        o = self.obj or obj

        self.commit_values[o] = val

    def set_commit_value_from_string(self, str_val, obj = None):
        o = self.obj or obj

        val = self.from_string(str_val)
        self.set_commit_values(val, o)

    def commit(self, if_different=True):
        for k, v in self.commit_values.iteritems():
            if if_different and (self.get_value(k) == v):
                continue
            self.set_value(k, v)

    def reset(self):
        self.commit_values = {}

    def get_value(self, obj=None):
        o = self.obj or obj
        if self.prop != None:
            return getattr(o, self.prop)

        mt = getattr(o, self.getter)
        return mt()

    def get_value_as_string(self, obj=None):
        o = self.obj or obj
        return self.to_string(self.get_value(o))

    def set_value(self, val, obj=None):
        o = self.obj or obj

        if self.is_read_only():
            raise("Property is read-only!")

        if self.prop != None:
            setattr(o, self.prop, val)
            return

        mt = getattr(o, self.setter)
        mt(val)

    def set_value_from_string(self, strval, obj=None):
        o = self.obj or obj

        val = self.from_string(strval)
        self.set_value(val, o)

    def is_read_only(self):
        return self.read_only


class DashboardPropertyMapper(DashboardPropertyMapperBase):
    def __init__(self, name, description, to_string, from_string, prop=None, getter=None, setter=None, read_only=True):
        super(DashboardPropertyMapper, self).__init__(name, description, to_string, from_string,
                                                      prop=prop, getter=getter, setter=setter, read_only=read_only)


class DashboardProperty(DashboardPropertyMapperBase):
    def __init__(self, obj, name, description, to_string, from_string, prop=None, getter=None, setter=None, read_only=True):
        super(DashboardProperty, self).__init__(name, description, to_string, from_string, obj=obj,
                                                prop=prop, getter=getter, setter=setter, read_only=read_only)
        if self.obj == None:
            raise Exception ("No object!")
