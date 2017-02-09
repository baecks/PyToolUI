from dashboardui.dashboard import Dashboard


class GraphDashboard(Dashboard):
    def __init__(self, title, description, lst):
        super(GraphDashboard, self).__init__(title, description = description, template = "graph_dashboard.html", data=lst)

    def get_additional_render_data(self):
        return {}
