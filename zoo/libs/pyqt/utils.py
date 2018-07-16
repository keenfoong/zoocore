from functools import partial

from qt import QtWidgets, QtGui, QtCore
from zoo.libs.utils import zlogging


def loggingMenu():
    logManager = zlogging.CentralLogManager()

    logMenu = QtWidgets.QMenu("logging")
    logs = dict(logManager.logs.items())

    for level in zlogging.levelsDict():
        levelAction = logMenu.addAction(level)
        levelAction.triggered.connect(partial(logManager.changeLevel, "root", level))
    logs.pop("root")
    logMenu.addSeparator()

    for name, log in iter(logs.items()):
        subMenu = logMenu.addMenu(name)
        for level in zlogging.levelsDict():
            levelAction = subMenu.addAction(level)
            levelAction.triggered.connect(partial(logManager.changeLevel, name, level))
    return logMenu


def iterParents(widget):
    parent = widget
    while True:
        parent = parent.parentWidget()
        if parent is None:
            break

        yield parent


def iterChildren(widget):
    """
    Yields all descendant widgets depth-first
    """
    for child in widget.children():
        yield child

        for grandchild in iterChildren(child):
            yield grandchild


def isNameInChildren(widgetName, parentWidget):
    for childWid in iterChildren(parentWidget):
        if childWid.objectName() == widgetName:
            return childWid


def hsvColor(hue, sat=1.0, val=1.0, alpha=1.0):
    """Create a QColor from the hsvaValues

    :param hue : Float , rgba

    """
    color = QtWidgets.QColor()
    color.setHsvF(hue, sat, val, alpha)
    return color


def colorStr(c):
    """Generate a hex string code from a QColor"""
    return ('%02x' * 4) % (c.red(), c.green(), c.blue(), c.alpha())

def hBoxLayout(parent=None):
    layout = QtWidgets.QHBoxLayout(parent)
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(1)
    return layout

def hframeLayout(parent=None):
    subFrame = QtWidgets.QFrame(parent=parent)
    layout = hBoxLayout(subFrame)
    subFrame.setLayout(layout)
    return subFrame, layout


def vframeLayout(parent=None):
    subFrame = QtWidgets.QFrame(parent=parent)
    layout = vBoxLayout(subFrame)
    subFrame.setLayout(layout)
    return subFrame, layout

def vBoxLayout(parent=None):
    layout = QtWidgets.QVBoxLayout(parent)
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(1)
    return layout

def hlineEdit(labelName, parent, enabled=True):
    layout = QtWidgets.QHBoxLayout()
    label = QtWidgets.QLabel(labelName, parent=parent)
    edit = QtWidgets.QLineEdit(parent=parent)
    edit.setEnabled(enabled)

    layout.addWidget(label)
    layout.addWidget(edit)
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(1)
    return label, edit, layout


def vlineEdit(labelName, parent, enabled=True):
    layout = QtWidgets.QVBoxLayout()
    label = QtWidgets.QLabel(labelName, parent=parent)
    edit = QtWidgets.QLineEdit(parent=parent)
    edit.setEnabled(enabled)
    layout.addWidget(label)
    layout.addWidget(edit)
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(1)
    return label, edit, layout


def recursivelySetActionVisiblity(menu, state):
    """Will recursively set the visible state of the QMenu actions

    :param menu: The QMenu to search
    :type menu: QMenu
    :type state: bool
    """
    for action in menu.actions():
        subMenu = action.menu()
        if subMenu:
            recursivelySetActionVisiblity(subMenu, state)
        elif action.isSeparator():
            continue
        if action.isVisible() != state:
            action.setVisible(state)
    if any(action.isVisible() for action in menu.actions()) and menu.isVisible() != state:
        menu.menuAction().setVisible(state)


def desktopPixmapFromRect(rect):
    """Generates a pixmap on the specified QRectangle.

    :param rect: Rectangle to Snap
    :type rect: :class:`~PySide.QtCore.QRect`
    :returns: Captured pixmap
    :rtype: :class:`~PySide.QtGui.QPixmap`
    """
    desktop = QtWidgets.QApplication.instance().desktop()
    return QtGui.QPixmap.grabWindow(desktop.winId(), rect.x(), rect.y(),
                                        rect.width(), rect.height())


def updateStyle(widget):
    """
    Updates a widget after an style object name change.
    eg. widget.setObjectName()
    :param widget:
    :return:
    """
    widget.setStyle(widget.style())


def windowFlagsString(windowFlags):
    """
    Returns a nice string that describes whats inside a windowFlags object

    Example:
        >>> print(windowFlagsString(self.windowFlags()))

        Prints out:
        QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowContextHelpButtonHint

    :param windowFlags:
    :return:
    """
    flag_type = (windowFlags & QtCore.Qt.WindowType_Mask)

    if flag_type == QtCore.Qt.Window:
        text = "QtCore.Qt.Window"
    elif flag_type == QtCore.Qt.Dialog:
        text = "QtCore.Qt.Dialog"
    elif flag_type == QtCore.Qt.Sheet:
        text = "QtCore.Qt.Sheet"
    elif flag_type == QtCore.Qt.Drawer:
        text = "QtCore.Qt.Drawer"
    elif flag_type == QtCore.Qt.Popup:
        text = "QtCore.Qt.Popup"
    elif flag_type == QtCore.Qt.Tool:
        text = "QtCore.Qt.Tool"
    elif flag_type == QtCore.Qt.ToolTip:
        text = "QtCore.Qt.ToolTip"
    elif flag_type == QtCore.Qt.SplashScreen:
        text = "QtCore.Qt.SplashScreen"
    else:
        text = ""

    if windowFlags & QtCore.Qt.MSWindowsFixedSizeDialogHint:
        text += "\n| QtCore.Qt.MSWindowsFixedSizeDialogHint"
    if windowFlags & QtCore.Qt.X11BypassWindowManagerHint:
        text += "\n| QtCore.Qt.X11BypassWindowManagerHint"
    if windowFlags & QtCore.Qt.FramelessWindowHint:
        text += "\n| QtCore.Qt.FramelessWindowHint"
    if windowFlags & QtCore.Qt.WindowTitleHint:
        text += "\n| QtCore.Qt.WindowTitleHint"
    if windowFlags & QtCore.Qt.WindowSystemMenuHint:
        text += "\n| QtCore.Qt.WindowSystemMenuHint"
    if windowFlags & QtCore.Qt.WindowMinimizeButtonHint:
        text += "\n| QtCore.Qt.WindowMinimizeButtonHint"
    if windowFlags & QtCore.Qt.WindowMaximizeButtonHint:
        text += "\n| QtCore.Qt.WindowMaximizeButtonHint"
    if windowFlags & QtCore.Qt.WindowCloseButtonHint:
        text += "\n| QtCore.Qt.WindowCloseButtonHint"
    if windowFlags & QtCore.Qt.WindowContextHelpButtonHint:
        text += "\n| QtCore.Qt.WindowContextHelpButtonHint"
    if windowFlags & QtCore.Qt.WindowShadeButtonHint:
        text += "\n| QtCore.Qt.WindowShadeButtonHint"
    if windowFlags & QtCore.Qt.WindowStaysOnTopHint:
        text += "\n| QtCore.Qt.WindowStaysOnTopHint"
    if windowFlags & QtCore.Qt.WindowStaysOnBottomHint:
        text += "\n| QtCore.Qt.WindowStaysOnBottomHint"
    if windowFlags & QtCore.Qt.CustomizeWindowHint:
        text += "\n| QtCore.Qt.CustomizeWindowHint"

    return text