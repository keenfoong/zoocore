import abc
from functools import partial

from zoo.libs import iconlib
from zoo.libs.utils import zlogging
from zoo.libs.pyqt.qt import QtWidgets, QtGui, QtCore

logger = zlogging.getLogger(__name__)


class CommandUi(QtWidgets.QWidget):
    """CommandUi class deals with encapsulating a command as a widget
    """
    triggered = QtCore.Signal(str)
    __metaclass__ = abc.ABCMeta

    def __init__(self, command):
        self.command = command
        self.item = None

    @abc.abstractmethod
    def create(self, parent=None):
        pass


class MenuItem(CommandUi):
    def create(self, parent=None):
        from maya import cmds
        uiData = self.command.uiData
        self.item = cmds.menuItem(l=uiData["uiData"], bld=uiData.get("bold", False), parent=parent,
                                  itl=uiData.get("italicized", False), c=partial(self.triggered.emit, self.command.id))


class CommandAction(CommandUi):
    def create(self, parent=None):
        uiData = self.command.uiData
        self.item = QtWidgets.QWidgetAction(parent=parent)
        text = uiData.get("label", "NOLABEL")
        actionLabel = QtWidgets.QLabel(text)
        self.item.setDefaultWidget(actionLabel)

        if self.color:
            actionLabel.setStyleSheet(
                "QLabel {" + " background-color: {}; color: {};".format(uiData.get("backgroundColor", ""),
                                                                        uiData.get("color", "")) + "}")
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
