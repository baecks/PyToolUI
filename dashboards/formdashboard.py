from .dashboards import Dashboard, DashboardAction
from .propertyproxy import PropertyProxy
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
    def __init__(self, title, description, obj):
        super(FormDashboard, self).__init__(title, description, template = "form_dashboard.html", **{'form_object':obj})

        #self.controls = {}

class DashboardFormEditAction(DashboardAction):
    def __init__(self, ob):
        super(DashboardFormEditAction, self).__init__(ob)
        self.obj = ob

    def execute(self):
        return FormDashboard("Coordinates Editor", "Allows editing coordinates", self.obj)

class FormDashboardSubmitAction(DashboardAction):
    def __init__(self, *args, **kwargs):
        super(FormDashboardSubmitAction, self).__init__(*args, **kwargs)

    def execute(self):
        self.commit_properties()
        return FormDashboard("Coordinates Editor - submitted", "Allows editing coordinates", self.obj)

