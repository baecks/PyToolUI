from dashboards.dashboards import Dashboard

class SimpleTableDashboard(Dashboard):
    def __init__(self, lst, title = None, description = None, editable=False):
        super(SimpleTableDashboard, self).__init__(title, description = description, template = "simple_table.html", rows=lst)
        self.editable = editable

    def get_additional_render_data(self):
        return {'editable' : self.editable}
