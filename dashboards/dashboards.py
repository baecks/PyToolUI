from .internal.dashboardbase import DashboardBase

class DashboardGroup(object):
    def __init__(self, title):
        self.title = title
        self._dashboards_and_groups = []

    def add(self, dashboard):
        if dashboard == None:
            raise Exception("No dashboard or group provided!")

        if not isinstance(dashboard, DashboardBase) and not isinstance(dashboard, DashboardGroup):
            raise Exception("No valid dashboard or group provided!")

        self._dashboards_and_groups.append(dashboard)

    def get_all(self):
        return self._dashboards_and_groups

class Dashboard(DashboardBase):
    def __init__(self, title, **kwargs):
        super(Dashboard,self).__init__(title, **kwargs)

