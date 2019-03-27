from functools import partial

from qt import QtWidgets, QtGui, QtCore

from zoo.libs.pyqt import uiconstants
from zoo.libs.utils import zlogging


def loggingMenu():
    logManager = zlogging.CentralLogManager()

    logMenu = QtWidgets.QMenu("logging")
    logs = dict(logManager.logs.items())

    for level in zlogging.levelsDict():
        levelAction = logMenu.addAction(level)
        levelAction.triggered.connect(partial(logManager.changeLevel, "root", level))
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
    layout.setSpacing(2)
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


def vBoxLayout(parent=None, margins=(2, 2, 2, 2), spacing=2):
    layout = QtWidgets.QVBoxLayout(parent)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
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
    """Updates a widget after an style object name change.
    eg. widget.setObjectName()

    :param widget:
    :return:
    """
    widget.setStyle(widget.style())


def setStylesheetObjectName(widget, name, update=True):
    """ Sets the widget to have the object name as set in the stylesheet

    ..code-block css

        #redselection {
            background-color: red;
        }

    ..code-block python

        btn = QtWidgets.QPushButton("Hello World")
        utils.setStylesheetObjectName(btn, "redselection")

    :param widget: Widget to apply object name to
    :param name: The object name in stylesheet without the '#'
    :return:
    """
    widget.setObjectName(name)
    if update:
        updateStyle(widget)


def windowFlagsString(windowFlags):
    """ Returns a nice string that describes what's inside a windowFlags object

    .. code-block:: python

        print(windowFlagsString(self.windowFlags()))

    Prints out:

    .. code-block:: python

        QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowSystemMenuHint
            | QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowContextHelpButtonHint

    :param windowFlags:
    :return:
    """
    flagTypes = [QtCore.Qt.Window,
                 QtCore.Qt.Dialog,
                 QtCore.Qt.Sheet,
                 QtCore.Qt.Drawer,
                 QtCore.Qt.Popup,
                 QtCore.Qt.Tool,
                 QtCore.Qt.ToolTip,
                 QtCore.Qt.SplashScreen]

    # Window Flag types
    windowFlagTypes = [QtCore.Qt.MSWindowsFixedSizeDialogHint,
                       QtCore.Qt.X11BypassWindowManagerHint,
                       QtCore.Qt.FramelessWindowHint,
                       QtCore.Qt.WindowTitleHint,
                       QtCore.Qt.WindowSystemMenuHint,
                       QtCore.Qt.WindowMinimizeButtonHint,
                       QtCore.Qt.WindowMaximizeButtonHint,
                       QtCore.Qt.WindowCloseButtonHint,
                       QtCore.Qt.WindowContextHelpButtonHint,
                       QtCore.Qt.WindowShadeButtonHint,
                       QtCore.Qt.WindowStaysOnTopHint,
                       QtCore.Qt.WindowStaysOnBottomHint,
                       QtCore.Qt.CustomizeWindowHint]
    text = ""

    # Add to text if flag type found
    flagType = (windowFlags & QtCore.Qt.WindowType_Mask)
    for t in flagTypes:
        if t == flagType:
            text += str(t)
            break

    # Add to text if the flag is found
    for wt in windowFlagTypes:
        if windowFlags & wt:
            text += "\n| {}".format(str(wt))

    return text


def alignmentString(alignmentFlags):
    """ Returns a nice string that describes what's inside a alignment object

    :param alignmentFlags: Alignment flags
    :return:
    """
    # Window Flag types
    windowFlagTypes = [QtCore.Qt.AlignLeft,
                       QtCore.Qt.AlignHCenter,
                       QtCore.Qt.AlignRight,
                       QtCore.Qt.AlignTop,
                       QtCore.Qt.AlignVCenter,
                       QtCore.Qt.AlignBottom]
    text = ""

    # Add to text if the flag is found
    for wt in windowFlagTypes:
        if alignmentFlags & wt:
            text += "{} | ".format(str(wt))

    return text


def dpiScale(value):
    """Resize by value based on current DPI

    :param value: the default 2k size in pixels
    :type value: int
    :return value: the size in pixels now dpi monitor ready (4k 2k etc)
    :rtype value: int
    """
    mult = QtWidgets.QApplication.desktop().logicalDpiY() / uiconstants.DEFAULT_DPI
    return value * mult


def dpiScaleDivide(value):
    """Inverse resize by value based on current DPI, for values that may get resized twice

    :param value: the size in pixels
    :type value: int
    :return value: the divided size in pixels
    :rtype value: int
    """
    mult = QtWidgets.QApplication.desktop().logicalDpiY() / uiconstants.DEFAULT_DPI
    if value != 0:
        return value / mult
    else:
        return value


def marginsDpiScale(left, top, right, bottom):
    """ Convenience function to return contents margins

    :param left:
    :param top:
    :param right:
    :param bottom:
    :return:
    """
    return (dpiScale(left), dpiScale(top), dpiScale(right), dpiScale(bottom))


def pointByDpi(point):
    """ Scales the QPoint by the current dpi scaling from maya.

    :param point: The QPoint to Scale by the current dpi settings
    :type point: QtCore.QPoint
    :return: The newly scaled QPoint
    :rtype: QtCore.QPoint
    """

    return QtCore.QPoint(dpiScale(point.x()), dpiScale(point.y()))


def sizeByDpi(size):
    """Scales the QSize by the current dpi scaling from maya.

    :param size: The QSize to Scale by the current dpi settings
    :type size: QSize
    :return: The newly scaled QSize
    :rtype: QSize
    """
    return QtCore.QSize(dpiScale(size.width()), dpiScale(size.height()))


def clearLayout(layout):
    """Clear the elements of a layout

    :param layout:
    :return:
    """

    item = layout.takeAt(0)
    while item:
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

        item = layout.takeAt(0)


def layoutItems(layout):
    """ Retrieves the items from the layout and returns it as a list

    :param layout: The layout to retrieve the items from
    :return: List of items from layout
    :rtype: list
    """
    return [layout.itemAt(i) for i in xrange(layout.count())]


def layoutWidgets(layout):
    """ Retrieves the widgets from the layout and returns it as a list

    :param layout: The layout to retrieve the widgets from
    :return: List of widgets from layout
    :rtype: list
    """
    return [layout.itemAt(i).widget() for i in xrange(layout.count())]
