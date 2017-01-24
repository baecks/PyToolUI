from tools.tools import Tool, ToolGroup
from core.toolserver import ToolServer

b = Tool('Tool 1')
g = ToolGroup('Group T')
c = Tool('Tool 2', g)
c = Tool('Tool 3', g)

ToolServer('Tool Server')