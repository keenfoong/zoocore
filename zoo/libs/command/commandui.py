from functools import partial

from zoo.libs import iconlib
from zoo.libs.utils import zlogging
from zoo.libs.pyqt.qt import QtWidgets, QtGui, QtCore

logger = zlogging.getLogger(__name__)


class CommandUi(QtCore.QObject):
    """CommandUi class deals with encapsulating a command as a widget
    """
    triggered = QtCore.Signal(str)

    def __init__(self, command):
        super(CommandUi, self).__init__()
        self.command = command
        self.item = None

    def create(self, parent=None):
        pass


class MenuItem(CommandUi):
    def create(self, parent=None):
        from maya import cmds
        uiData = self.command.uiData()
        self.item = cmds.menuItem(l=uiData["uiData"], bld=uiData.get("bold", False), parent=parent,
                                  itl=uiData.get("italicized", False), c=partial(self.triggered.emit, self.command.id))


class CommandAction(CommandUi):
    def create(self, parent=None):
        uiData = self.command.uiData()
        self.item = QtWidgets.QWidgetAction(parent)
        text = uiData.get("label", "NOLABEL")
        actionLabel = QtWidgets.QLabel(text)
        self.item.setDefaultWidget(actionLabel)
        color = uiData.get("color", "")
        backColor = uiData.get("backgroundColor", "")
        if color or backColor:
            actionLabel.setStyleSheet(
                "QLabel {background-color: %s; color: %s;}" % (backColor,
                                                               color))
        icon = uiData.get("icon")
        if icon:
            if isinstance(icon, QtGui.QIcon):
                self.item.setIcon(icon)
            else:
                icon = iconlib.icon(icon)
                if not icon.isNull():
                    self.item.setIcon(icon)
        self.item.setStatusTip(uiData.get("tooltip"))
        self.item.triggered.connect(partial(self.triggered.emit, self.command.id))
        logger.debug("Added commandUi, {}".format(text))
        return self.item

    def show(self):
        if self.item is not None:
            self.item.show()
