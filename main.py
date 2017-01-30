from core.dashboardserver import DashboardServer
from dashboards.propertymapping import DashboardString, DashboardInt, DashboardList, DashboardObject
from dashboards.dashboards import DashboardGroup
from dashboards.simpletabledashboard import SimpleTableDashboard

class Test(object):
    def __init__(self, t, v):
        self.t = t
        self.v = v

test_name = DashboardString('t', 'Name', 'Name of the person involved.')
test_age = DashboardInt('v', 'Age', 'Age of the person.')
o = DashboardObject('test_obj', (test_name, test_age), "Name and Age Info", "This is the name and age of persons, just as test.")

lst = [Test('Sven', 41), Test('Martine', 35), Test('Emma', 10), Test('Viktor', 5), Test('Thibe', 5)] * 20

wlst = DashboardList("List", o, "List of NameAge objects", "List of all members of the household", lst)

g = DashboardGroup("Test boards")
dashboard = SimpleTableDashboard(wlst, "Table of household members")
g.add(dashboard)

#
# g = DashboardGroup('Tests')
#
#
# data = Test('Sven Baeck', 41)
# f = FormDashboard('Form dashboard', 'Testing the FormDashBoard.', group=g)
# nameProperty = BoundDashboardString(data, "Name", "The full name of the person", prop="t")
# ageProperty = BoundDashboardInt(data, "Age", "Age of the person", prop="v")
# f.addTextControl(nameProperty)
# f.addCheckboxControl(ageProperty, 41, 0)
# f.addRadioControl(ageProperty, (41,42,43), ("age 41", "age 42", "age 43"))
# f.addPasswordControl(nameProperty)
#
# b = SimpleTableDashboard('Simple Table Test', "This test is intended to verify and demonstrate the SimpleTableDashboard.", lst, group=g, editor=f)
# nameMapping = UnboundDashboardStringReference('First name', "First name of the person", 't')
# ageMapping = UnboundDashboardPropertyInt('Age', "Age of the person", 'v')
# b.addMapping(nameMapping)
# b.addMapping(ageMapping)

DashboardServer('Dashboard Tester', g)