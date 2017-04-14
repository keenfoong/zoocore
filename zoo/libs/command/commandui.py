import abc
from zoo.libs import iconlib
from zoo.libs.utils import zlogging
from zoo.libs.pyqt.qt import QtWidgets, QtGui, QtCore

logger = zlogging.getLogger(__name__)


class CommandUi(QtWidgets.QWidget):
    """CommandUi class deals with encapsulating a command as a widget
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, command):
        self.command = command

    @abc.abstractmethod
    def create(self):
        pass


class CommandAction(CommandUi):
    triggered = QtCore.Signal()

    def create(self):
        uiData = self.command.uiData()
        newAction = QtWidgets.QWidgetAction()
        text = uiData.get("label", "NOLABEL")
        actionLabel = QtWidgets.QLabel(text)
        newAction.setDefaultWidget(actionLabel)

        if self.color:
            actionLabel.setStyleSheet(
                "QLabel {" + " background-color: {}; color: {};".format(uiData.get("backgroundColor", ""), uiData.get("color", "")) + "}")
        icon = uiData.get("icon")
        if icon:
            if isinstance(icon, QtGui.QIcon):
                newAction.setIcon(icon)
            else:
                icon = iconlib.icon(icon)
                if not icon.isNull():
                    newAction.setIcon(icon)
        newAction.setStatusTip(uiData.get("tooltip"))
        newAction.triggered.connect(self.triggered.emit)
        logger.debug("Added commandUi, {}".format(text))
        return newAction
