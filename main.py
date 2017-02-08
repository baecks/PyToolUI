from core.dashboardserver import DashboardServer
from dashboards.dashboards import DashboardGroup
from dashboards.propertyproxy import PropertyProxy, ObjectProxy, ListProxy
from dashboards.simpletabledashboard import SimpleTableDashboard
from dashboards.formdashboard import FormDashboard
#
# act = DashboardAction(1,2,3,a="test",b=9.8)
# DashboardAction.test_url_path(act.url)


#
# def foo(a,b=5,*args,**kwargs):
#     for i,j in kwargs.items():
#         print ("kwarg " + i + " = " + str(j))
#     for a in args:
#         print ("arg " + str(a))
#
# foo(1,2,3,q=6)
#
# import inspect
# a = inspect.getfullargspec(foo)
#

class tt(object):
    def __init__(self,i,j):
        self.x = i
        self.y = j
        self.active = True

lst = [tt(i+1,(i+1)*5) for i in range(50)]

class ttProxy(ObjectProxy):
    def __init__(self, obj):
        super(ttProxy, self).__init__("Coordinate", "These are coordinates on a map by x and y.")
        self.xc = PropertyProxy("X coordinate", 'This is the x coordinate', obj, 'x').set_value_list_constraint({1:"Position 1" , 2 : "Position 2", 3 : "Position 3"})
        self.yc = PropertyProxy("Y coordinate", 'This is the y coordinate', obj, 'y').set_hidden_constraint()
        self.active = PropertyProxy("Active", 'This property defines whether the coordinates are active', obj, 'active')

ttList = ListProxy("Coordinates", "List of coordinates.", ttProxy, lst)

el = ttList.get_element_by_index(0)
#el.xc.value = -1


g = DashboardGroup("Test boards")

dashboard = SimpleTableDashboard("Coordinates", "Table of coordinates in the list", ttList, editable=True)
form = FormDashboard("Coordinates Editor", "Allows editing coordinates", ttList.get_element_by_index(5))

g2 = DashboardGroup("Test actions")
g2.add(dashboard)
g2.add(form)

g.add(g2)
g.add(dashboard)
g.add(form)

DashboardServer('Dashboard Tester', 'This application is available for testing and debugging the DASHBOARD UI framework.', g)