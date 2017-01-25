from dashboards import Dashboard

class SimpleTableDashboard(Dashboard):
    def __init__(self, name, description, list, group = None):
        super(SimpleTableDashboard, self).__init__(name, "simple_table.html", group)
        self.rows = list
        self.description = description

