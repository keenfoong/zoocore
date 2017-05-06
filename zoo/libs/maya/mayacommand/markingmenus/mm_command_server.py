from zoo.libs.command import executor
from zoo.libs.maya.api import scene
from zoo.libs.maya.mayacommand.markingmenus import markingmenu
from zoo.libs.utils import classtypes

from maya.api import OpenMaya as om2


class CommandServer(object):
    __metaclass__ = classtypes.Singleton

    def __init__(self):
        self.executor = executor.Executor()
        self.layoutRegistry = markingmenu.LayoutRegistry()
        self.layoutRegistry.registryLayoutByEnv("ZOO_COMMAND_LAYOUT_PATHS")

    def findLayout(self, id):
        try:
            return self.layoutRegistry.layouts[id]
        except KeyError:
            return None

    def markingMenuRequest(self, layouts):
        """
        :param layouts: 
        :type layouts: list
        :return: 
        :rtype: 
        """
        base = layouts[0]
        for layout in iter(layouts[1:]):
            base = base.merge(layout)
        menu = markingmenu.MarkingMenu(layout=base, commandExecutor=self.executor, name=base.id)
        menu.create()
        return menu

    def runtimeMarkingMenuCallback(self):
        """Marking menus for hive are always based on having a node selected.
        Marking menus discovery is based on what selection you have for example by selecting
        a rig control, this method will find the connected meta node for the component and see
        if it has specified tools, it will also travel up to the rig meta node and do the same check.
        based on this those tools aka layouts will be configured and a new marking menu will be 
        created in the scene
        """
        selection = scene.getSelectedNodes()
        if not selection:
            return False
        layouts = []
        for n in iter(selection):
            dep = om2.MFnDependencyNode(n)
            try:
                lay = self.findLayout(dep.findPlug("zoo_command").asString())
            except RuntimeError:
                continue
            if lay:
                layouts.append(lay)
        if not layouts:
            return False
        return self.markingMenuRequest(layouts)
