
from dashboards.simpletabledashboard import SimpleTableDashboard
from dashboards.formdashboard import FormDashboard
from dashboards.dashboards import DashboardGroup
from core.dashboardserver import DashboardServer
from dashboards.propertymapping import DashboardPropertyMapperString, DashboardPropertyMapperInt, DashboardPropertyString, DashboardPropertyInt

class Test(object):
    def __init__(self, t, v):
        self.t = t
        self.v = v

lst = [Test('Sven', 41), Test('Martine', 35), Test('Emma', 10), Test('Viktor', 5), Test('Thibe', 5)] * 20

g = DashboardGroup('Tests')
b = SimpleTableDashboard('Simple Table Test', "This test is intended to verify and demonstrate the SimpleTableDashboard.", lst, group=g)
nameMapping = DashboardPropertyMapperString('First name', "First name of the person", 't')
ageMapping = DashboardPropertyMapperInt('Age', "Age of the person", 'v')
b.addMapping(nameMapping)
b.addMapping(ageMapping)

data = Test('Sven Baeck', 41)
f = FormDashboard('Form dashboard', 'Testing the FormDashBoard.', group=g)
nameProperty = DashboardPropertyString(data, "Name", "The full name of the person", prop="t")
ageProperty = DashboardPropertyInt(data, "Age", "Age of the person", prop="v")
f.addTextControl(nameProperty)
f.addCheckboxControl(ageProperty, 41, 0)

DashboardServer('Dashboard Tester')