from dashboards import Dashboard
import copy, types

def _is_checked(self):
        return self.get_commit_value() == self.check_value

def _is_radio_option_checked(self, option):
        return self.get_commit_value() == option.value

class RadioOptions(object):
    def __init__(self, value, label):
        self.value = value
        self.label = label

class FormDashboard(Dashboard):
    def __init__(self, title, **kwargs):
        super(FormDashboard, self).__init__(title, template = "form_dashboard.html")
        self.controls = {}

    def _add_control(self, m, control_type, param_name=None):
        m2 = copy.copy(m)
        m2.control = control_type
        self.addMapping(m2)
        # if isinstance(m2, DashboardPropertyMapper):
        #     # it is a mapping object. Hence need to know which parameter to use at runtime
        #     if (param_name == None) or (len(param_name) < 1) or (param_name.find(' ') >= 0):
        #         raise ("No valid parameter name provided for control %s" % m2.name)
        #     self._add_parameter_mapping(param_name, m2)

        return m2

    def addTextControl(self, m, param_name=None):
        self._add_control(m, 'text', param_name=param_name)

    def addPasswordControl(self, m, param_name=None):
        self._add_control(m, 'password', param_name=param_name)

    def addCheckboxControl(self, m, check_value, uncheck_value, param_name=None):
        m2 = self._add_control(m, 'checkbox', param_name=param_name)
        m2.check_value = check_value
        m2.uncheck_value = uncheck_value
        m2.checked = types.MethodType(_is_checked, m2)

    def addRadioControl(self, m, values, labels, param_name=None):
        m2 = self._add_control(m, 'radio', param_name=param_name)
        m2.options = []
        try:
            for i in range(len(values)):
                m2.options.append(RadioOptions(values[i], labels[i]))
        except Exception as e:
            raise Exception("Failed to create radio control: %s" % str(e))
        m2.checked = types.MethodType(_is_radio_option_checked, m2)

    def setParameters(self, params):
        # for all checkbox controls, if the name of the control is not present in the list of parameters,
        # assume it is unchecked. This is standard behaviour in HTML forms. Unchecked checkboxes do not
        # appear in the submitted parameters.
        for c in self.mapping:
            try:
                if c.control == 'checkbox':
                    if not c.name in params:
                        c.set_value(c.uncheck_value)
            except:
                pass

        super(FormDashboard, self).setParameters(self, params)