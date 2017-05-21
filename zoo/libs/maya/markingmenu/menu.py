import os
import pprint

from zoo.libs.pyqt.embed import mayaui
from zoo.libs.utils import file
from zoo.libs.utils import classtypes
from zoo.libs.utils import general

from maya import cmds


class LayoutRegistry(object):
    __metaclass__ = classtypes.Singleton

    def __init__(self):
        self.layouts = {}

    def registryLayoutByEnv(self, env):
        paths = os.environ[env].split(os.pathsep)
        for p in paths:
            for root, dirs, files in os.walk(p):
                for f in files:
                    if f.endswith(".layout"):
                        data = file.loadJson(os.path.join(root, f))
                        self.layouts[data["id"]] = Layout(data)


class Layout(object):
    def __init__(self, data):
        self.data = data
        self.id = data["id"]

    def __repr__(self):
        return "Layout: {}".format(pprint.pformat(self.data))

    def __getitem__(self, item):
        return self.data.get(item)

    def __iter__(self):
        for name, data in iter(self.data.items()):
            yield name, data

    def items(self):
        return self.data["items"].items()

    def merge(self, layout):
        self.data = general.merge(self.data, layout.data["items"])
        self.solve()

    def solve(self):
        registry = LayoutRegistry()
        solved = False
        for item, data in self.data.items():
            if isinstance(data, basestring):
                if data.startswith("@"):
                    subLayout = registry.layouts.get(data)
                    subLayout.solve()
                    self.data[item] = subLayout
                    solved = True
                    continue
        return solved


class MarkingMenu(object):
    def __init__(self, layout, name, parent):
        self.description = ""
        self.name = name
        self.parent = parent
        self.popMenu = None
        self.actions = []
        self.layout = layout
        self.options = {"allowOptionBoxes": False,
                        "altModifier": False,
                        "button": 1,
                        "ctrlModifier": False,
                        "postMenuCommandOnce": True,
                        "shiftModifier": False}

    def asQObject(self):
        return mayaui.toQtObject(self.name)

    def create(self):
        if cmds.popupMenu(self.name, exists=True):
            cmds.deleteUI(self.name)

        self.popMenu = cmds.popupMenu(self.name, parent=self.parent,
                                      markingMenu=True, postMenuCommand=self._show, **self.options)
        return self

    def _show(self, menu, parent):

        cmds.setParent(menu, m=True)
        cmds.menu(menu, e=True, dai=True)
        self.show(self.layout, menu, parent)

    def kill(self):
        if cmds.popupMenu(self.name, ex=True):
            cmds.deleteUI(self.name)

    def _buildGeneric(self, data, menu, parent):
        # @todo come up with a similar approach as the commands version so we can have generic operations without commands
        pass

    def show(self, layout, menu, parent):
        # @todo come up with a similar approach as the commands version so we can have generic operations without commands
        pass

    def allowOptionBoxes(self):
        return cmds.popupMenu(self.name, q=True, allowOptionBoxes=True)

    def altModifier(self):
        return cmds.popupMenu(self.name, q=True, altModifier=True)

    def button(self):
        return cmds.popupMenu(self.name, q=True, button=True)

    def ctrlModifier(self):
        return cmds.popupMenu(self.name, q=True, ctrlModifier=True)

    def deleteAllItems(self):
        try:
            cmds.popupMenu(self.name, e=True, deleteAllItems=True)
        except Exception:
            return False
        return True

    def exists(self):
        return cmds.popupMenu(self.name, exists=True)

    def itemArray(self):
        return cmds.popupMenu(self.name, q=True, itemArray=True)

    def markingMenu(self):
        return cmds.popupMenu(self.name, q=True, markingMenu=True)

    def numberOfItems(self):
        return cmds.popupMenu(self.name, q=True, numberOfItems=True)

    def postMenuCommand(self, command):
        cmds.popupMenu(self.name, e=True, postMenuCommand=command)

    def postMenuCommandOnce(self, state):
        cmds.popupMenu(self.name, e=True, postMenuCommandOnce=state)

    def shiftModifier(self):
        return cmds.popupMenu(self.name, q=True, shiftModifier=True)

    def setShiftModifier(self, value):
        return cmds.popupMenu(self.name, e=True, shiftModifier=value)

    def setParent(self, parent):
        return cmds.popupMenu(self.name, e=True, parent=parent.objectName())

    def setCtrlModifier(self, value):
        return cmds.popupMenu(self.name, e=True, ctrlModifier=value)

    def setAltModifier(self, state):
        return cmds.popupMenu(self.name, e=True, altModifier=state)

    def setUseLeftMouseButton(self):
        return cmds.popupMenu(self.name, e=True, button=1)

    def setUseRightMouseButton(self):
        return cmds.popupMenu(self.name, e=True, button=2)

    def setUseMiddleMouseButton(self):
        return cmds.popupMenu(self.name, e=True, button=3)
