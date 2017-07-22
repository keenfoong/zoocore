from zoo.libs.toolpalette import palette
from zoo.libs.utils import env


def show():
    parent = None
    if env.isInMaya():
        from zoo.libs.pyqt.embed import mayaui
        parent = mayaui.getMayaWindow()
    print parent
    tools = palette.ToolPalette(parent=parent)
    tools.createMenus()
    return tools
