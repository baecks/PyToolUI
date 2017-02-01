from core.dashboardserver import DashboardServer
from dashboards.dashboards import DashboardGroup
from dashboards.propertyproxy import PropertyProxy, ObjectProxy, ListProxy
from dashboards.simpletabledashboard import SimpleTableDashboard


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

lst = [tt(i+1,(i+1)*5) for i in range(50)]

class ttProxy(ObjectProxy):
    def __init__(self, obj):
        super(ttProxy, self).__init__("Coordinate", "These are coordinates on a map by x and y.")
        self.xc = PropertyProxy("X coordinate", 'This is the x coordinate', obj, 'x')
        self.yc = PropertyProxy("Y coordinate", 'This is the y coordinate', obj, 'y')

ttList = ListProxy("Coordinates", "List of coordinates.", ttProxy, lst)

g = DashboardGroup("Test boards")
dashboard = SimpleTableDashboard(ttList, "Table of coordinates",editable=True)
g.add(dashboard)

DashboardServer('Dashboard Tester', g)