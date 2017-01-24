from internal.toolbase import ToolBase

class Tool(ToolBase):
    def __init__(self, name, group = None):
        super(Tool, self).__init__(name)

        if group != None:
            group.addTool(self)
        else:
            ToolGroup.tools_and_groups.append(self)

class ToolGroup(ToolBase):
    tools_and_groups = []

    def __init__(self, name):
        super(ToolGroup, self).__init__(name)
        self.tools = []
        ToolGroup.tools_and_groups.append(self)

    def addTool(self, t):
        if t == None:
            return
        if not isinstance(t, Tool):
            raise Exception ("The object is not a valid Tool instance!")

        self.tools.append(t)

