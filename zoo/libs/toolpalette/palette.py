import os
import abc
import traceback
from functools import partial

import time

from zoo.libs import iconlib
from zoo.libs.pyqt import utils
from zoo.libs.pyqt.qt import QtGui, QtWidgets
from zoo.libs.plugin import pluginmanager
from zoo.libs.utils import flush
from zoo.libs.utils import zlogging
from zoo.libs.utils import file
from zoo.libs.plugin import plugin

logger = zlogging.getLogger(__name__)


class ToolPalette(pluginmanager.PluginManager):
    TOOLSENV = "TOOL_PALETTE_DEFINITION"
    LAYOUTENV = "TOOL_PALETTE_LAYOUT"

    def __init__(self, parent=None):
        super(ToolPalette, self).__init__()
        self.parent = parent
        self.subMenus = {}
        # builds the environment for zap plugin
        self.menuName = "Zoo Tools"
        self.menu = None
        self.layout = {}
        self.loadAllPlugins()
        self._loadLayouts()

    def removePreviousMenus(self):
        """Removes Any zoo plugin menu from maya by iterating through the children of the main window looking for any
        widget with the objectname Zoo Tools.
        """
        for childWid in utils.iterChildren(self.parent):
            if childWid.objectName() == self.menuName:
                childWid.deleteLater()

    def createMenus(self):
        """Loops through all loadedPlugins and creates a menu/action for each. Uses the plugin class objects parent
        variable to determine where  it sits within the menu.
        """
        self.removePreviousMenus()
        self.menu = self.parent.menuBar().addMenu(self.menuName)
        self.menu.setTearOffEnabled(True)
        self.menu.setObjectName(self.menuName)
        # load the layout
        for i in iter(self.layout["menu"]):
            if isinstance(i, basestring) and "separator" in i:
                self.menu.addSeparator()
                continue
            self._menuCreator(self.menu, i)
        # build developer menu
        devMenu = self.menu.addMenu("Developer")
        devMenu.setTearOffEnabled(True)
        logMenu = utils.loggingMenu()
        devMenu.addMenu(logMenu)
        reloadAction = devMenu.addAction("ShutDown")
        reloadAction.setIcon(iconlib.icon("shutdown"))
        self.menu.addSeparator()
        self.subMenus["Developer"] = devMenu
        reloadAction.triggered.connect(self.shutdown)
        versionAction = self.menu.addAction("Version: {}".format(os.environ.get("ZOO_TOOL_VERSION", "")))
        versionAction.setEnabled(False)
        # a fix for 2016
        self.parent.menuBar().show()

    def _menuCreator(self, parentMenu, data):
        menu = self.getMenu(data["name"])
        if menu is None:
            menu = parentMenu.addMenu(data["name"])
            menu.setTearOffEnabled(True)
            self.subMenus[data["name"]] = menu

        for i in iter(data["children"]):
            if isinstance(i, dict):
                self._menuCreator(menu, i)
            self._addAction(i, menu)

    def _addAction(self, pluginId, parent):
        plugin = self.pluginFromId(pluginId)
        uiData = plugin.uiData()
        label = uiData.get("label", "No_label")
        newAction = QtWidgets.QWidgetAction(self.parent)
        actionLabel = QtWidgets.QLabel(label)
        newAction.setDefaultWidget(actionLabel)

        icon = uiData.get("icon")
        color = uiData.get("color", "")
        backgroundColor = uiData.get("backgroundColor", "")
        if color:
            label.setStyleSheet("QLabel {" + " background-color: {}; color: {};".format(backgroundColor, color) + "}")
        if icon:
            if isinstance(icon, QtGui.QIcon):
                newAction.setIcon(icon)
            else:
                icon = iconlib.icon(icon)
                if not icon.isNull():
                    newAction.setIcon(icon)
        newAction.setStatusTip(uiData.get("tooltip", ""))
        newAction.triggered.connect(partial(self.executePlugin, plugin))
        parent.addAction(newAction)
        logger.debug("Added action, {}".format(label))

    def shutdown(self):
        """Shutdown's all of zoo triggers the reloads zoo code.
        """
        self.teardown()
        flush.reloadZoo()
        from zoo.libs.toolpalette import run
        zoo = run.show()
        zoo.createMenus()

    def executePluginByName(self, name):
        if name in self.loadedPlugins:
            plugin = self.loadedPlugins[name]
            self.executePlugin(plugin)

    def executePlugin(self, plugin):
        plugin._execute()
        logger.debug("Execution time:: {}".format(plugin.stats.executionTime))

    def executeAll(self):
        """Calls the execute method on all currently loaded plugins
        """
        for plugin in self.loadedPlugins.itervalues():
            plugin.execute()

    def teardown(self):
        logger.debug("Attempting to teardown plugins")
        for plugName, plug in self.loadedPlugins.items():
            plug.teardown()
            logger.debug("shutting down tool -> {}".format(plug.displayName))
            self.unload(plugName)
        self.plugins = {}
        if self.menu:
            logger.debug("Closing menu-> %s" % self.menuName)
            self.removePreviousMenus()
            self.menu = None

    def getMenu(self, menuName):
        """Returns the menu object if it exists else None.
        :param menuName: str, the menuName to retrieve.
        :return: QMenu.
        """
        if menuName == self.menu.objectName():
            return self.menu
        return self.subMenus.get(menuName)

    def pluginFromId(self, id):
        for i in iter(self.loadedPlugins.values()):
            if i.id == id:
                return i

    def _loadLayouts(self):
        self.registerPaths(paths=os.environ.get(ToolPalette.TOOLSENV, "").split(os.pathsep))
        paletteLayout = os.environ.get(ToolPalette.LAYOUTENV, "").split(os.pathsep)
        if not paletteLayout:
            raise ValueError("No Layout configuration has been defined")
        layout = {}
        for f in iter(paletteLayout):
            with file.loadFile(f) as layout:
                l = file.loadJson(layout)
                layout.update(l)
        self.layout = layout


class ToolDefinition(plugin.Plugin):
    __metaclass__ = abc.ABCMeta

    def __init__(self, manager=None):
        super(ToolDefinition, self).__init__(manager)
        self.tool = None

    @abc.abstractproperty
    def id(self):
        pass

    @staticmethod
    def uiData():
        return {"icon": "",
                "tooltip": "",
                "label": ""}

    @abc.abstractproperty
    def creator(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def teardown(self):
        pass

    def _execute(self):
        self.stats.startTime = time.time()
        try:
            self.execute()
            self.stats.finish()
        except:
            tb = traceback.format_exc()
            self.stats.finish(tb)
            raise
