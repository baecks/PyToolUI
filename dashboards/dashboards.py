from internal.dashboardbase import DashboardBase

class DashboardGroup(DashboardBase):
    _dashboards_and_groups = []
    _dashboards_by_name = {}

    def __init__(self, name):
        super(DashboardGroup, self).__init__(name, None)
        DashboardGroup.addDashboard(self)
        self.dashboards = []

    @staticmethod
    def addDashboard(dashboard, group=None):
        if group != None:
            group.dashboards.append(dashboard)
        else:
            DashboardGroup._dashboards_and_groups.append(dashboard)

        if not isinstance(dashboard, DashboardGroup):
            # it's a dashboard
            DashboardGroup._dashboards_by_name[dashboard.name] = dashboard

    @staticmethod
    def getDashboardHierarchy():
        return DashboardGroup._dashboards_and_groups

    @staticmethod
    def findDashboardByName(name):
        try:
            return DashboardGroup._dashboards_by_name[name]
        except:
            return None

class Dashboard(DashboardBase):
    def __init__(self, name, template, group = None, mapping=None):
        super(Dashboard,self).__init__(name, template, group, mapping)
        DashboardGroup.addDashboard(self, group)

