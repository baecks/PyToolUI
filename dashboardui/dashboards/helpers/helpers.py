import importlib
import numbers

def get_class_from_name(class_name):
    try:
        parts = class_name.split('.')
        module_name = ".".join(parts[:-1])
        mod = importlib.import_module(module_name)
        cls = getattr(mod, parts[-1])
        return cls
    except:
        raise Exception("Failed to process the class name (%s)!" % str(class_name))

def is_numerical(value):
    if value == None:
        raise Exception("No value provided!")
    return isinstance(value, numbers.Number)
