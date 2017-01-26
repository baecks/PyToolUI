from dashboards import Dashboard
import copy, types, inspect

def _is_checked(self):
        return self.get_commit_value() == self.check_value

def _is_radio_option_checked(self, option):
        return self.get_commit_value() == option.value

class RadioOptions(object):
    def __init__(self, value, label):
        self.value = value
        self.label = label

class FormDashboard(Dashboard):
    def __init__(self, name, description, group = None):
        super(FormDashboard, self).__init__(name, "form_dashboard.html", group)
        self.controls = {}
        self.description = description

    def _add_control(self, m, control_type):
        m2 = copy.copy(m)
        m2.control = control_type
        self.addMapping(m2)
        return m2

    def addTextControl(self, m):
        self._add_control(m, 'text')

    def addCheckboxControl(self, m, check_value, uncheck_value):
        m2 = self._add_control(m, 'checkbox')
        m2.check_value = check_value
        m2.uncheck_value = uncheck_value
        m2.checked = types.MethodType(_is_checked, m2)

    def addRadioControl(self, m, values, labels):
        m2 = self._add_control(m, 'radio')
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