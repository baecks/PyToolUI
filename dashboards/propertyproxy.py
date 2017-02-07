import threading, inspect
import numbers
from .helpers import is_numerical
import re
import cherrypy

class BaseProxy(object):
    _id2obj_lock = threading.RLock()
    _id2obj_global_dict = {}

    @staticmethod
    def _remember(obj):
        oid = str(id(obj))
        BaseProxy._id2obj_lock.acquire()
        BaseProxy._id2obj_global_dict[oid] = obj
        BaseProxy._id2obj_lock.release()
        return oid

    @staticmethod
    def _id2obj(oid):
        BaseProxy._id2obj_lock.acquire()
        obj = BaseProxy._id2obj_global_dict[oid]
        BaseProxy._id2obj_lock.release()
        return obj

    @staticmethod
    def getPropertyById(oid):
        return BaseProxy._id2obj(oid)

    def __init__(self, label, description):
        self.label = label
        self.description = description
        self.uid = PropertyProxy._remember(self)
        self._transactional = False

    def commit(self, if_different=True):
        pass

    def reset(self):
        pass

    def validate(self):
        pass

class PropertyProxy(BaseProxy):
    def __init__(self, label, description, proxied_object, proxied_property):
        super(PropertyProxy, self).__init__(label, description)
        self.proxied_object = proxied_object
        self.proxied_property = proxied_property
        self._non_sessioned_commit_value = None

        # Constraints
        self.clear_all_constraints()

    # The commit value
    def _get_commit_value(self):
        try:
            ses = cherrypy.session
        except:
            return self._non_sessioned_commit_value

        try:
            return ses['_commit_value_'+self.uid]
        except:
            return None

    def _set_commit_value(self, v):
        try:
            ses = cherrypy.session
            ses['_commit_value_'+self.uid] = v
        except:
            self._non_sessioned_commit_value = v

    _commit_value = property(fget=_get_commit_value, fset=_set_commit_value)

    def get_value(self):
        return self._commit_value or getattr(self.proxied_object, self.proxied_property)

    def _get_property_type(self):
        try:
            return type(getattr(self.proxied_object, self.proxied_property))
        except:
            raise Exception("Failed to determine type for property!")

    def _get_property_type_as_string(self):
        return self._get_property_type().__name__

    def set_value(self, value):
        if isinstance(value, str):
            prop_type = self._get_property_type_as_string()

            try:
                cls = globals()['__builtins__'][prop_type]
            except AttributeError:
                pass
                # For the moment, non built-in types are not supported for properties
                # TODO: Might want to make one exception for date-time
                # if not, separate module and class
                #module, prop_type = prop_type.rsplit(".", 1)
                #module = importlib.import_module(module)
                #cls = getattr(module, prop_type)

            try:
                value_to_set = cls(value)
            except:
                raise Exception("Failed to convert value from string (%s)!" % value)
        else:
            value_to_set = value

        # Check the constraints
        self._evaluate_constraints(value_to_set)

        if not self._transactional:
            setattr(self.proxied_object, self.proxied_property, value_to_set)
        else:
            self._commit_value = value_to_set

    def commit(self, if_different=True):
        if not self._transactional:
            return

        if if_different:
            if (getattr(self.proxied_object, self.proxied_property) == self._commit_value):
                return
        setattr(self.proxied_object, self.proxied_property, self._commit_value)
        self.reset()

    def reset(self):
        self._commit_value = None

    def _set_transactional(self, transactional):
        self._transactional = transactional

    value = property(fget=get_value,fset=set_value)

# Constraints
    def _evaluate_constraints(self, value):
        # value list constraint
        if self.constraint_value_dict != None:
            if not value in self.constraint_value_dict.keys():
                raise Exception("The value is not in the constraint value list!")

        # range constraint
        if self.constraint_range_low != None:
            if (value < self.constraint_range_low) or (value > self.constraint_range_high):
                raise Exception("The value is not in the constraint range!")

        # regex constraint
        if self.constraint_regex_pattern != None:
            if self.constraint_regex_pattern.match(value) == None:
                raise Exception("The value doesn't match the regex constraint!")

    # Value list constraint
    def clear_value_list_constraint(self):
        self.constraint_value_dict = None
        return self

    def set_value_list_constraint(self, value_list):
        """

        Args:
            value_list: This can be either a list of values allowed for set operations or a dictionnary mapping values to string labels
            for presentation in a dashboard.

        Returns:

        """
        if value_list == None:
            raise Exception("No value list provided!")

        prop_type = self._get_property_type()
        value_dict = {}

        if isinstance(value_list, list):
            for v in value_list:
                if not isinstance(v, prop_type):
                    raise Exception("The list contains a value of different type then the proxied property (%s)" % str(v))
                value_dict[v]=v
            self.constraint_value_dict = value_dict
            return self

        if isinstance(value_list, dict):
            for v, l in value_list.items():
                if not isinstance(v, prop_type):
                    raise Exception("The dictionary contains a value of different type then the proxied property (%s)" % str(v))
                if not isinstance(l, str):
                    raise Exception("The dictionary contains a non-string label (%s)" % str(l))
                value_dict[v]=l
            self.constraint_value_dict = value_dict
            return self

        return self # allows chaining constraints

    # Range constraint
    def clear_range_constraint(self):
        self.constraint_range_low = None
        self.constraint_range_high = None
        return self # allows chaining constraints

    def set_range_constraint(self, low, high):
        # This constraint is possible only for numerical properties
        prop_type = self._get_property_type()
        if not issubclass(prop_type, numbers.Number):
            raise Exception("This constraint can only be applied to numerical properties!")

        if low == None:
            raise Exception("No low value provided!")
        if high == None:
            raise Exception("No high value provided!")

        if not is_numerical(low):
            raise Exception("The low value is non-numerical!")
        if not is_numerical(high):
            raise Exception("The high value is non-numerical!")

        if high <= low:
            raise Exception("The high value should be higher than the low value!")

        self.constraint_range_low = low
        self.constraint_range_high = high

        return self # allows chaining constraints

    # REGEX constraint
    def clear_regex_constraint(self):
        self.constraint_regex_pattern = None
        return self # allows chaining constraints

    def set_regex_constraint(self, regex):
        if regex == None:
            raise Exception("No regex provided!")

        if not issubclass(self._get_property_type(), str):
            raise Exception("A regex constraint can only be applied to string properties!")

        try:
            self.constraint_regex_pattern = re.compile(regex)
        except Exception as e:
            raise Exception("No valid regex provided (%s)!" % str(e))

        return self # allows chaining constraints

    # BOOL value mapped constraint
    # This constraint assumes the variable can have 2 values. The first to be interpreted as boolean TRUE,
    # the second as boolean FALSE. This is actually a hint for display in dashboards.
    def clear_bool_value_mapped_constraint(self):
        self.constraint_value_dict = None
        self.constraint_is_boolean_mapped = False
        return self

    def set_bool_value_mapped_constraint(self, bool_true_value, bool_false_value):
        if bool_true_value == None:
            raise Exception("No value provided for mapping to TRUE!")
        if bool_false_value == None:
            raise Exception("No value provided for mapping to FALSE!")

        prop_type = self._get_property_type()
        if not isinstance(bool_true_value, prop_type):
            raise Exception("The TRUE mapping value is not of the correct type (%s)!" % self._get_property_type_as_string() )
        if not isinstance(bool_false_value, prop_type):
            raise Exception("The FALSE mapping value is not of the correct type (%s)!" % self._get_property_type_as_string() )

        self.constraint_value_dict = [bool_true_value, bool_false_value]
        self.constraint_is_boolean_mapped = True

        return self # allows chaining constraints

    # Constraint to signal that the value should never by displayed (e.g. passwords)
    def set_hidden_constraint(self):
        self.hidden = True
        return self

    def clear_hidden_constraint(self):
        self.hidden = False
        return self

    def clear_all_constraints(self):
        self.clear_bool_value_mapped_constraint()
        self.clear_range_constraint()
        self.clear_regex_constraint()
        self.clear_value_list_constraint()
        self.clear_hidden_constraint()

    @property
    def boolean(self):
        prop_type = self._get_property_type()
        if issubclass(prop_type, bool):
            return True
        return self.constraint_is_boolean_mapped

    @property
    def boolean_values(self):
        prop_type = self._get_property_type()
        if issubclass(prop_type, bool):
            return [True, False]
        if self.constraint_is_boolean_mapped:
            return self.constraint_value_dict

        return []

    @property
    def list_constrained(self):
        return self.constraint_value_dict != None

    @property
    def numerical(self):
        return is_numerical(self.get_value())

    @property
    def low_range(self):
        return self.constraint_range_low

    @property
    def high_range(self):
        return self.constraint_range_high


class ObjectProxy(BaseProxy):
    def __setattr__(self, item, value):
        """
        If the attribute being set is a sub-type from BaseProxy, set it to be transactional. This is required
        for proper validation and commit to the data being wrapped.

        Args:
            item: Name of the attribute
            value: Attribute value

        Returns:
            None
        """
        if isinstance(value, BaseProxy):
            value._set_transactional(True)
            try:
                self._attribute_names_ordered.append(item)
            except:
                pass

        super(BaseProxy, self).__setattr__(item, value)

    def __init__(self, label, description, **kwargs):
        super(ObjectProxy, self).__init__(label, description)
        self._attribute_names_ordered = []
        for n, v in kwargs.items():
            setattr(self, n, v)

    def _get_base_proxy_attribs(self):
        return [getattr(self, x) for x in self._attribute_names_ordered]

    def _set_transactional(self, transactional):
        """
        Recursively pass on setting the transactional flag
        Args:
            transactional: Boolean defining if set operations should be handled transactional or not

        Returns:
            None
        """
        attribs_to_process = self._get_base_proxy_attribs()
        for a in attribs_to_process:
            attribs_to_process.set_transactional(transactional)

    def commit(self, if_different=True):
        self.validate()

        attribs_to_commit = self._get_base_proxy_attribs()
        for a in attribs_to_commit:
            a.commit(if_different)
        self.reset()

    def reset(self):
        attribs_to_reset = self._get_base_proxy_attribs()
        for a in attribs_to_reset:
            a.reset()

    def validate(self):
        attribs_to_validate = self._get_base_proxy_attribs()
        for a in attribs_to_validate:
            a.validate()

        self.validate_object()

    def validate_object(self):
        """
        This method can be overridden to provide dedicated consistency checking on the attribute values in the
        object. In case of a problem an exception is to be raised.

        Returns:
            None
        """
        pass

    def get_property_labels(self):
        return [x.label for x in self._get_base_proxy_attribs()]

    def __iter__(self):
        return iter(self._get_base_proxy_attribs())

    def __len__(self):
        return len(self._get_base_proxy_attribs())

#    attributes = property(fget=_get_base_proxy_attribs)

class ListProxy(BaseProxy):
    def __init__(self, label, description, object_class, lst):
        """

        Args:
            label:
            description:
            object_class:
            lst: Every element in the list should either be a singled object in case the object_class
             takes just one parameter. If it requires multiple parameters, each list element should be a list/tuple.
             The number of elements in each list/tuple should be equal to the number of parameters required
             to create an instance of object_class.

        Returns:
            None
        """
        super(ListProxy, self).__init__(label, description)
        if object_class == None:
            raise("No class to map the list elements provided!")
        if not inspect.isclass(object_class):
            raise ("The object class provided is not a valid class!")
        if not issubclass(object_class, BaseProxy):
            raise ("The object class provided is not a sub-class of %s!" % BaseProxy.__name__)
        if object_class == BaseProxy:
            raise("The class %s can't be used to map list elements!" % BaseProxy.__name__)

        if lst == None:
            raise("No list of elements to map provided!")
        if not self._is_elem_iterable(lst):
            raise("The object to be mapped is not a valid list (not iterable)!")

        self._elements = []
        for e in lst:
            # Test if single object or list/tuple
            try:
                if self._is_elem_iterable(e):
                    # it is a list or tuple
                    wrapped_elem = object_class(*e)
                else:
                    # single object
                    wrapped_elem = object_class(e)
            except Exception as e:
                raise Exception("Failed to create an instance of %s (%s)!" % (object_class.__name__, str(e)))
            self._elements.append(wrapped_elem)

    def _is_elem_iterable(self, e):
        try:
            it = iter(e)
        except TypeError:
            # Single object
            return False

        return True

    def __iter__(self):
        return iter(self._elements)

    def __len__(self):
        return len(self._elements)

    def _get_element_property_labels(self):
        if len(self._elements) == 0:
            return []
        return self._elements[0].get_property_labels()

    def get_element_by_index(self, index):
        try:
            elem = self._elements[index]
            return elem
        except:
            raise Exception("Requesting an invalid index!")

    property_labels = property(fget=_get_element_property_labels)

