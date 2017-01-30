import copy, keyword, re
import threading
import cherrypy

# _objects_by_ref = {}
# _ref_by_object = {}
#
# def _add_object(o):
#     global _objects_by_ref, _ref_by_object
#     ref = "obj_%d" % len(_objects_by_ref)+1
#     _objects_by_ref[ref] = o
#     _ref_by_object[o] = ref
#
#     return ref
#
# def _reset_object_references():
#     global _objects_by_ref, _ref_by_object
#     _objects_by_ref = []
#     _ref_by_object = []
#
# def _get_object_by_ref(ref):
#     global _objects_by_ref
#     return _objects_by_ref[ref]
#
# def _get_object_by_ref(o):
#     global _ref_by_object
#     return _ref_by_object[o]


#TODO: Clean-up of this administration still to be implemented!
class DashboardPropertyBase(object):
    _id2obj_lock = threading.RLock()
    _id2obj_global_dict = {}

    @staticmethod
    def _remember(obj):
        oid = id(obj)
        DashboardPropertyBase._id2obj_lock.acquire()
        DashboardPropertyBase._id2obj_global_dict[oid] = obj
        DashboardPropertyBase._id2obj_lock.release()
        return oid

    @staticmethod
    def _id2obj(oid):
        DashboardPropertyBase._id2obj_lock.acquire()
        obj = DashboardPropertyBase._id2obj_global_dict[int(oid)]
        DashboardPropertyBase._id2obj_lock.release()
        return obj

    @staticmethod
    def getPropertyById(oid):
        return DashboardPropertyBase._id2obj(oid)

    def __init__(self, property_name, label = None, description = None, obj = None):
        """

        Args:
            property_name: This is the name of the property.
            label:
            description:
            obj:
        """
        self.oid = DashboardPropertyBase._remember(self)
        self.uid = self.oid

        self.property_name = property_name
        self.is_valid_python_attribute_name(self.property_name)

        self.bound_object = obj
        self.label = label
        if (self.label == None):
            self.label = self.property_name.replace("_", " ").capitalize()
        elif (len(self.label) < 1):
            raise Exception("Invalid property label!")
        label_pattern = r'[^\a-zA-Z0-9 ]' # letters, digits and space
        if re.search(label_pattern, self.label):
            raise Exception("Property label \"%s\" contains illegal characters!" % self.label)

        self.description = description

    def is_valid_python_attribute_name(self, n):
        if (n == None):
            raise Exception("No name specified!")
        if (keyword.iskeyword(n)):
            raise Exception("Name %s is a keyword!" % n)
        if (n in dir(__builtins__)):
            raise Exception("Name %s is a built-in!" % n)
        if (len(n) < 1):
            raise Exception("A name should at least be 1 character!")
        name_pattern = r'[^\a-zA-Z0-9_]'
        if re.search(name_pattern, n):
            raise Exception("Name \"%s\" contains illegal characters!" % n)

    def is_bound(self):
        return self.bound_object != None

    def check_bound(self):
        if not self.is_bound():
            raise("The property is unbound!")

    def bind(self, o):
        if(o == None):
            raise Exception("Can't bind to a 'None' object!")

        if self.is_bound():
            raise Exception("This property is already bound!")

        bound_prop = copy.copy(self)
        bound_prop.bound_object = o
        return bound_prop

    def commit(self, if_different=True):
        raise Exception("Method \"commit\" is not implemented!")

