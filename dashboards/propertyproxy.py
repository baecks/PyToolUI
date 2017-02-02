import threading, inspect

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
        self.commit_value = None

    def get_value(self):
        return self.commit_value or getattr(self.proxied_object, self.proxied_property)

    def set_value(self, value):
        if isinstance(value, str):
            try:
                prop_type = type(getattr(self.proxied_object, self.proxied_property)).__name__
            except:
                raise Exception("Failed to determine type for property!")

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

        if not self._transactional:
            setattr(self.proxied_object, self.proxied_property, value_to_set)
        else:
            self.commit_value = value_to_set

    def commit(self, if_different=True):
        if not self._transactional:
            return

        if if_different:
            if (getattr(self.proxied_object, self.proxied_property) == self.commit_value):
                return
        setattr(self.proxied_object, self.proxied_property, self.commit_value)
        self.reset()

    def reset(self):
        self.commit_value = None

    def _set_transactional(self, tranactional):
        self._transactional = tranactional

    value = property(fget=get_value,fset=set_value)

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

    property_labels = property(fget=_get_element_property_labels)