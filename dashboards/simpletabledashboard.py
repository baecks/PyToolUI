from .internal.dashboardbase import DashboardBase

class SimpleTableDashboard(DashboardBase):
    def __init__(self, lst, title = None):
        super(SimpleTableDashboard, self).__init__(title, template = "simple_table.html", rows=lst)
