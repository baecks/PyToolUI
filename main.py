from core.dashboardserver import DashboardServer
from dashboards.propertymapping import DashboardString, DashboardInt, DashboardList, DashboardObject
from dashboards.dashboards import DashboardGroup
from dashboards.simpletabledashboard import SimpleTableDashboard

from dashboards.internal.propertyproxy import PropertyProxy, ObjectProxy, ListProxy

class tt(object):
    def __init__(self,i,j):
        self.x = i
        self.y = j

lst = [tt(i+1,(i+1)*5) for i in range(10)]

class ttProxy(ObjectProxy):
    def __init__(self, obj):
        super(ObjectProxy, self).__init__("Coordinate", "These are coordinates on a map by x and y.")
        self.xc = PropertyProxy("X coordinate", 'This is the x coordinate', obj, 'x')
        self.yc = PropertyProxy("Y coordinate", 'This is the y coordinate', obj, 'y')

ttList = ListProxy("Coordinates", "List of coordinates.", ttProxy, lst)

g = DashboardGroup("Test boards")
dashboard = SimpleTableDashboard(ttList, "Table of coordinates")
g.add(dashboard)

DashboardServer('Dashboard Tester', g)