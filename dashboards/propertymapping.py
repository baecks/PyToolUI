from internal.propertymappingbase import DashboardPropertyMapper, DashboardProperty

# Property mapping for strings
class DashboardPropertyMapperString(DashboardPropertyMapper):
    def __init__(self, name, description, prop=None, getter=None, setter=None, read_only=True):
        super(DashboardPropertyMapperString, self).__init__(name, description, lambda x : x, lambda x : x, prop, getter, setter, read_only)

class DashboardPropertyString(DashboardProperty):
    def __init__(self, obj, name, description, prop=None, getter=None, setter=None, read_only=True):
        super(DashboardPropertyString, self).__init__(obj, name, description, lambda x : x, lambda x : x, prop, getter, setter, read_only)


# Property mapping for integers
class DashboardPropertyMapperInt(DashboardPropertyMapper):
    def __init__(self, name, description, prop=None, getter=None, setter=None, read_only=True):
        super(DashboardPropertyMapperInt, self).__init__(name, description, lambda x : str(x), lambda x : int(x), prop, getter, setter, read_only)

class DashboardPropertyInt(DashboardProperty):
    def __init__(self, obj, name, description, prop=None, getter=None, setter=None, read_only=True):
        super(DashboardPropertyInt, self).__init__(obj, name, description, lambda x : str(x), lambda x : int(x), prop, getter, setter, read_only)
