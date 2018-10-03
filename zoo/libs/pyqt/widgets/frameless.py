from qt import QtWidgets, QtCore, QtGui

from preferences.interface import prefutils
from zoo.libs import iconlib

from zoo.libs.pyqt import utils as qtutils, utils
from zoo.libs.pyqt.widgets import extendedbutton, iconmenu, mainwindow
from zoo.libs.utils import zlogging, colour
from zoo.preferences import preference

logger = zlogging.getLogger(__name__)


class ResizeDirection:
    """ Flag attributes to tell the what position the resizer is """
    Left = 1
    Top = 2
    Right = 4
    Bottom = 8


class FramelessWindow(mainwindow.MainWindow):
    """ Custom window with the frame removed, with our own customizations
    """

    closed = QtCore.Signal()
    dockChanged = QtCore.Signal(object)
    windowResizedFinished = QtCore.Signal()

    def __init__(self, title="", parent=None, width=100, height=100, framelessChecked=True, titleBarClass=None):
        """ Frameless Window

        :param title:
        :param parent:
        :param width:
        :param height:
        :param framelessChecked:
        """
        self.topResize = VerticalResize()
        self.botResize = VerticalResize()
        self.rightResize = HorizontalResize()
        self.leftResize = HorizontalResize()
        self.topLeftResize = CornerResize()
        self.topRightResize = CornerResize()
        self.botLeftResize = CornerResize()
        self.botRightResize = CornerResize()

        self.resizers = [self.topResize, self.topRightResize, self.rightResize,
                         self.botRightResize, self.botResize, self.botLeftResize,
                         self.leftResize, self.topLeftResize]

        super(FramelessWindow, self).__init__(title=title, parent=parent, width=width, height=height,
                                              showOnInitialize=False, transparent=True)

        for r in self.resizers:
            r.setParent(self)

        #self.window().setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.framelessChecked = framelessChecked

        if titleBarClass is not None:
            self.titleBar = titleBarClass(self)
        else:
            self.titleBar = FramelessTitleBar(self)

        self.windowLayout = QtWidgets.QGridLayout(self)
        self.windowContents = FramelessWindowContents(self)
        self.initFramelessUi()

        self.framelessConnections()
        self.initWindowLayout()
        self.currentDocked = None
        self.setProperty("framelessWindow", True)
        self.setDefaultStyleSheet()
        self.setWindowTitle(title)

        # This could be done better
        if not framelessChecked:
            self.setResizerActive(False)
        else:
            self.setFrameless(True, force=True)


    def initFramelessUi(self):

        # Setup resizers
        for r in self.resizers:
            r.windowResizedFinished.connect(self.windowResizedFinished)

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCustomCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.windowLayout)

        # Window settings
        self.setMouseTracking(True)

        self.setResizeDirections()

    def setWindowTitle(self, title):
        super(FramelessWindow, self).setWindowTitle(title)
        if hasattr(self, "titleBar"):
            self.titleBar.setTitleText(title)

    def setDefaultStyleSheet(self):
        """Try to set the default stylesheet, if not, just ignore it

        :return:
        """
        try:
            from zoo.preferences.core import preference
        except ImportError:
            return

        coreInterface = preference.interface("core_interface")
        try:
            result = coreInterface.stylesheet()
        except ValueError:
            pass

        self.setStyleSheet(result.data)

    def closeEvent(self, ev):
        super(FramelessWindow, self).closeEvent(ev)

    def setFrameless(self, frameless=True, force=False):
        """Use this to turn off frameless if need be

        :param frameless:
        """
        #if self.bootstrapWidget() is None:
        #    logger.warning("FramelessWindow.setFrameless() Can't set frameless when bootstrap not set up! Ignoring.")
        #    return

        window = self.window()
        # Set Frameless
        if frameless and not self.isFrameless():

            window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            window.setWindowFlags(window.windowFlags() | QtCore.Qt.FramelessWindowHint)
            self.setResizerActive(True)
        elif not frameless and self.isFrameless():
            # Set not frameless
            window.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
            window.setWindowFlags(window.windowFlags() ^ QtCore.Qt.FramelessWindowHint)
            self.setResizerActive(False)

        window.show()

    def setTitleBarIconSize(self, size):
        """ Set Icon size of the title icon

        :param size:
        :type size: QtCore.QSize
        :return:
        """
        self.titleBar.setIconSize(size)

    def setWindowStyleSheet(self, style):
        """Set the style sheet of the window

        :param style:
        :return:
        """
        #if not self.isDocked():
        #    self.window().setStyleSheet(style)

        self.setStyleSheet(style)

    def connectMinimizeButton(self, connect):
        """Connect minimize button

        :param connect:
        :return:
        """
        self.titleBar.minimizeButton.leftClicked.connect(connect)

    def isFrameless(self):
        """Checks to see if the FramelessWindowHint flag in windowFlags
        """
        return self.window().windowFlags() & QtCore.Qt.FramelessWindowHint == QtCore.Qt.FramelessWindowHint

    def resizerHeight(self):
        """Calculates the total height of the vertical resizers
        """
        resizers = [self.topResize, self.botResize]
        ret = 0
        for r in resizers:
            if not r.isHidden():
                ret += r.minimumSize().height()

        return ret

    def resizerWidth(self):
        """ Calculates the total width of the vertical resizers
        """
        resizers = [self.leftResize, self.rightResize]
        ret = 0
        for r in resizers:
            if not r.isHidden():
                ret += r.minimumSize().width()

        return ret

    def setResizerActive(self, active):
        """Enable or disable the resizers

        :param active:
        """

        if active:
            for r in self.resizers:
                r.show()
        else:
            for r in self.resizers:
                r.hide()

    def initWindowLayout(self):
        """Initialise the window layout. Eg the title, the side resizers and the contents
        """

        self.windowLayout.addWidget(self.titleBar, 1, 1, 1, 1)
        self.windowLayout.addWidget(self.windowContents, 2, 1, 1, 1)
        self.windowLayout.setHorizontalSpacing(0)
        self.windowLayout.setVerticalSpacing(0)

        self.windowLayout.setContentsMargins(0, 0, 0, 0)

        self.windowLayout.addWidget(self.topLeftResize, 0, 0, 1, 1)
        self.windowLayout.addWidget(self.topResize, 0, 1, 1, 1)
        self.windowLayout.addWidget(self.topRightResize, 0, 2, 1, 1)

        self.windowLayout.addWidget(self.leftResize, 1, 0, 2, 1)
        self.windowLayout.addWidget(self.rightResize, 1, 2, 2, 1)

        self.windowLayout.addWidget(self.botLeftResize, 3, 0, 1, 1)
        self.windowLayout.addWidget(self.botResize, 3, 1, 1, 1)
        self.windowLayout.addWidget(self.botRightResize, 3, 2, 1, 1)

        self.windowLayout.setColumnStretch(1, 1)
        self.windowLayout.setRowStretch(2, 1)

    def setResizeDirections(self):
        """Set the resize directions for the resize widgets for the window
        """
        # Horizontal/Vertical Resizers
        self.topResize.setResizeDirection(ResizeDirection.Top)
        self.botResize.setResizeDirection(ResizeDirection.Bottom)
        self.rightResize.setResizeDirection(ResizeDirection.Right)
        self.leftResize.setResizeDirection(ResizeDirection.Left)

        # Corner Resizers
        self.topLeftResize.setResizeDirection(ResizeDirection.Left | ResizeDirection.Top)
        self.topRightResize.setResizeDirection(ResizeDirection.Right | ResizeDirection.Top)
        self.botLeftResize.setResizeDirection(ResizeDirection.Left | ResizeDirection.Bottom)
        self.botRightResize.setResizeDirection(ResizeDirection.Right | ResizeDirection.Bottom)

    def framelessConnections(self):
        self.dockChanged.connect(self.dockEvent)

    def setMaximiseVisible(self, vis=True):
        self.titleBar.setMaximiseVisible(vis)

    def setMinimiseVisible(self, vis=True):
        self.titleBar.setMinimiseVisible(vis)

    def setMainLayout(self, layout):
        self.windowContents.setLayout(layout)

    def showEvent(self, event):
        """
        When the frameless window gets showed
        :param event:
        :return:
        """
        # Triggering docking changed because couldn't get MayaQWidgetDockableMixin.floatingChanged() to work
        if self.isDocked() != self.currentDocked:
            self.currentDocked = self.isDocked()
            self.dockChanged.emit(self.currentDocked)

        super(FramelessWindow, self).showEvent(event)

    def dockEvent(self, docked):
        """
        Ran when the window gets docked or undocked
        :param docked:
        :return:
        """
        if docked:
            self.setResizerActive(not docked)

    def settingsName(self):
        return self.objectName()

    def closeEvent(self, ev):
        self.closed.emit()


class FramelessTitleBar(QtWidgets.QFrame):
    """
    Title bar of the frameless window. Click drag this widget to move the window widget
    """
    def __init__(self, window=None, parent=None, showTitle=True):
        """

        :param window:
        :type window: :class:`FramelessWindow`
        :param parent: :class:`QtWidgets.QWidget`
        """
        super(FramelessTitleBar, self).__init__(parent=parent or window)

        self.mainLayout = qtutils.hBoxLayout(self)
        self.contentsLayout = qtutils.hBoxLayout(self)
        self.titleLayout = qtutils.hBoxLayout(self)

        self.frameless = window
        self.mousePos = None  # type: QtCore.QPoint
        self.widgetMousePos = None  # type: QtCore.QPoint

        # Title bar buttons
        self.logoButton = iconmenu.IconMenuButton(parent=self)

        iconColour = prefutils.stylesheetSettingColor("$WINDOW_LOGO_ICON_COLOR")
        self.setLogoIconName("zooToolsZ", iconColour, qtutils.dpiScale(20))
        self.titleButtonsLayout = qtutils.hBoxLayout(self)

        self.toggle = True

        self.iconSize = qtutils.dpiScale(20)
        col = (128, 128, 128)
        self.closeButton = extendedbutton.ExtendedButton(parent=self)
        self.closeButton.setIconByName("xMark", color=col, size=self.iconSize, colorOffset=80)
        self.minimizeButton = extendedbutton.ExtendedButton(parent=self)
        self.minimizeButton.setIconByName("minus", color=col, size=self.iconSize, colorOffset=80)
        self.maxButton = extendedbutton.ExtendedButton(parent=self)
        self.maxButton.setIconByName("checkbox", color=col, size=self.iconSize, colorOffset=80)
        self.titleLabel = FramelessTitleLabel()

        if not showTitle:
            self.titleLabel.hide()

        self.initUi()
        self.connections()

    def setLogoIconName(self, iconName, color, size):
        self.logoButton.setIconByName(iconName, color, size, 30)

    def initUi(self):

        # Button Settings
        btns = [self.closeButton, self.minimizeButton, self.maxButton]
        for b in btns:
            b.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            b.setDoubleClickEnabled(False)

        # Layout
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self.mainLayout.setSpacing(0)

        self.titleLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)

        self.initLogoButton()

        self.titleButtonsLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.titleLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        self.titleButtonsLayout.setContentsMargins(0, qtutils.dpiScale(0), 0, 0)

        self.titleButtonsLayout.addLayout(self.titleLayout)
        self.titleButtonsLayout.addWidget(self.minimizeButton)
        self.titleButtonsLayout.addWidget(self.maxButton)
        self.titleButtonsLayout.addWidget(self.closeButton)
        self.titleButtonsLayout.setSpacing(qtutils.dpiScale(self.titleButtonsLayout.spacing()))

        self.mainLayout.addSpacing(qtutils.dpiScale(8))  # these spacings might cause issues down the line
        self.mainLayout.addWidget(self.logoButton)
        self.mainLayout.addSpacing(qtutils.dpiScale(8))
        self.mainLayout.addLayout(self.contentsLayout)  # Title bar contents layout if the user wants to add anything
        #self.mainLayout.addLayout(self.titleLayout)

        self.mainLayout.addLayout(self.titleButtonsLayout)
        self.mainLayout.addSpacing(qtutils.dpiScale(5))

        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.setContentsMargins(qtutils.dpiScale(5), qtutils.dpiScale(0), qtutils.dpiScale(20),0)

        self.mainLayout.setStretch(1, 1)

    def setTitleText(self, value):
        self.titleLabel.setText(value.upper())

    def connections(self):
        self.closeButton.leftClicked.connect(lambda: self.window().close())

    def initLogoButton(self):
        """Initialise logo button settings
        """
        self.logoButton.setIconSize(qtutils.sizeByDpi(QtCore.QSize(24, 24)))
        self.logoButton.setFixedSize(qtutils.sizeByDpi(QtCore.QSize(30, 40)))
        toggleFrameless = self.logoButton.addAction("Toggle Custom Window",
                                                    connect=self.setFramelessEnabled,
                                                    checkable=True)
        self.logoButton.addAction("Create 3D Characters")
        self.logoButton.addAction("Toggle Toolbars", connect=self.toggleContents)

        toggleFrameless.setChecked(self.frameless.framelessChecked)

    def setLogoButtonSize(self, size):
        pass

    def setWindowIconSize(self, size):
        """
        Sets the icon size of the titlebar icons
        :param size:
        :return:
        """
        self.iconSize = size

    def setFramelessEnabled(self, action=None):
        """ Enable frameless or switch back to operating system default.
        This is maya specific, may need to change this in the future. Will need to rework all this code

        :param action:
        :return:
        :rtype: FramelessWindow
        """

        from zoo.apps.toolpalette import run

        a = run.show()

        toolDef = a.pluginFromTool(self.frameless)
        print(toolDef)

        frameless = action.isChecked()

        toolDef.uiData['frameless']['frameless'] = frameless
        toolDef.uiData['frameless']['force'] = True
        rect = self.window().rect()
        pos = self.window().pos()


        self.window().close()

        toolDef._execute()

        newTool = toolDef.tool[-1]['tool']
        # Make sure the size and position is correct. Use a timer because doing it instantly doesn't work. Bit yucky D=
        QtCore.QTimer.singleShot(0, lambda: newTool.window().setGeometry(pos.x()+3,
                                                                         pos.y()+15,
                                                                         rect.width(),
                                                                         rect.height()))

        return newTool

    def setMaximiseVisible(self, show=True):
        """Set Maximise button visible

        :param show:
        """
        if show:
            self.maxButton.show()
        else:
            self.maxButton.hide()

    def setMinimiseVisible(self, show=True):
        """Set minimize button visibility

        :param show:
        """
        if show:
            self.minimizeButton.show()
        else:
            self.minimizeButton.hide()

    def toggleContents(self):
        """Show or hide the additional contents in the titlebar
        """
        if self.contentsLayout.count() > 0:
            for i in range(1, self.contentsLayout.count()):
                widget = self.contentsLayout.itemAt(i).widget()
                if widget.isHidden():
                    widget.show()
                else:
                    widget.hide()

    def mousePressEvent(self, event):
        """Mouse click event to start the moving of the window

        :type event: :class:`QtCore.QEvent`
        """
        if event.buttons() & QtCore.Qt.LeftButton:
            self.widgetMousePos = self.frameless.mapFromGlobal(QtGui.QCursor.pos())

    def mouseReleaseEvent(self, event):
        """Mouse release for title bar

        :type event: :class:`QtCore.QEvent`
        """
        self.widgetMousePos = None

    def mouseMoveEvent(self, event):
        """Move the window based on if the titlebar has been clicked or not

        :type event: :class:`QtCore.QEvent`
        """
        if self.widgetMousePos is None:
            return

        # If its normal windows mode, then disable mouseMove
        if not self.frameless.isFrameless():
            return

        pos = QtGui.QCursor.pos()
        newPos = pos

        newPos.setX(pos.x()-self.widgetMousePos.x())
        newPos.setY(pos.y()-self.widgetMousePos.y())

        self.window().move(newPos)


class FramelessWindowContents(QtWidgets.QFrame):
    """
    So we can have our custom css attributes
    """
    pass


class FramelessTitleLabel(QtWidgets.QLabel):
    """ For CSS purposes """
    pass


class WindowResizer(QtWidgets.QFrame):
    """
    The resize widgets for the sides of the windows and the corners to resize the parent window.

    """
    windowResized = QtCore.Signal()
    windowResizedFinished = QtCore.Signal()

    def __init__(self, parent):
        super(WindowResizer, self).__init__(parent=parent)
        self.initUi()
        self.direction = 0  # ResizeDirection
        self.widgetMousePos = None  # QtCore.QPoint
        self.widgetGeometry = None  # type: QtCore.QRect
        self.setStyleSheet("background:transparent;")

    def initUi(self):
        self.windowResized.connect(self.windowResizeEvent)

    def paintEvent(self, event):
        """ Mouse events seem to deactivate when its completely transparent. Hacky way to avoid that for now.

        :type event: :class:`QtCore.QEvent`
        """

        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(255, 0, 0, 1))
        painter.end()

    def leaveEvent(self, event):
        """ Turn the mouse back to original

        :type event: :class:`QtCore.QEvent`
        """
        QtWidgets.QApplication.restoreOverrideCursor()

    def mousePressEvent(self, event):
        self.widgetMousePos = self.mapFromGlobal(QtGui.QCursor.pos())
        self.widgetGeometry = self.window().frameGeometry()

    def mouseMoveEvent(self, event):
        self.windowResized.emit()

    def setParent(self, parent):
        """Set the parent and the window

        :param parent:
        """
        self.frameless = parent
        super(WindowResizer, self).setParent(parent)

    def windowResizeEvent(self):
        """ Resize based on the mouse position and the current direction
        """
        pos = QtGui.QCursor.pos()
        newGeometry = self.window().frameGeometry()

        # Minimum Size
        mW = self.window().minimumSize().width()
        mH = self.window().minimumSize().height()

        # Check to see if the ResizeDirection flag is in self.direction
        if self.direction & ResizeDirection.Left == ResizeDirection.Left:
            left = newGeometry.left()
            newGeometry.setLeft(pos.x() - self.widgetMousePos.x())
            if newGeometry.width() <= mW:  # Revert back if too small
                newGeometry.setLeft(left)
        if self.direction & ResizeDirection.Top == ResizeDirection.Top:
            top = newGeometry.top()
            newGeometry.setTop(pos.y() - self.widgetMousePos.y())
            if newGeometry.height() <= mH:  # Revert back if too small
                newGeometry.setTop(top)
        if self.direction & ResizeDirection.Right == ResizeDirection.Right:
            newGeometry.setRight(pos.x() + (self.minimumSize().width() - self.widgetMousePos.x()))
        if self.direction & ResizeDirection.Bottom == ResizeDirection.Bottom:
            newGeometry.setBottom(pos.y() + (self.minimumSize().height() - self.widgetMousePos.y()))

        # Set new sizes
        x = newGeometry.x()
        y = newGeometry.y()
        w = max(newGeometry.width(), mW)   # Minimum Width
        h = max(newGeometry.height(), mH)  # Minimum height

        self.window().setGeometry(x, y, w, h)

    def setResizeDirection(self, direction):
        """Set the resize direction. Expects an int from ResizeDirection
        
        .. code-block:: python

            setResizeDirection(ResizeDirection.Left | ResizeDirection.Top)

        :param direction: ResizeDirection
        :type direction: int
        """
        self.direction = direction

    def mouseReleaseEvent(self, event):
        self.windowResizedFinished.emit()


class CornerResize(WindowResizer):
    """ Resizers in the corner of the window

    """

    def __init__(self, parent=None):
        super(CornerResize, self).__init__(parent=parent)

    def initUi(self):
        super(CornerResize, self).initUi()

        self.setFixedSize(utils.sizeByDpi(QtCore.QSize(10, 10)))

    def enterEvent(self, event):
        """ Set cursor based on corner hovered

        :type event: :class:`QtCore.QEvent`
        """
        # Top Left or Bottom Right
        if self.direction == ResizeDirection.Left | ResizeDirection.Top or \
                        self.direction == ResizeDirection.Right | ResizeDirection.Bottom:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeFDiagCursor)

            # Top Right or Bottom Left
        elif self.direction == ResizeDirection.Right | ResizeDirection.Top or \
                        self.direction == ResizeDirection.Left | ResizeDirection.Bottom:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeBDiagCursor)


class VerticalResize(WindowResizer):
    """ Resizers for the top and bottom of the window

    """
    def __init__(self, parent=None):
        super(VerticalResize, self).__init__(parent=parent)

    def initUi(self):
        super(VerticalResize, self).initUi()
        self.setFixedHeight(utils.dpiScale(8))

    def enterEvent(self, event):
        """Change cursor on hover

        :type event: :class:`QtCore.QEvent`
        """
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeVerCursor)


class HorizontalResize(WindowResizer):
    """ Resizers for the left and right of the window

    """
    def __init__(self, parent=None):
        super(HorizontalResize, self).__init__(parent=parent)

    def initUi(self):
        super(HorizontalResize, self).initUi()
        self.setFixedWidth(utils.dpiScale(8))

    def enterEvent(self, event):
        """Change cursor on hover

        :type event: :class:`QtCore.QEvent`
        """
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeHorCursor)


def getFramelessWindows():
    """ Gets all frameless windows in the scene

    :return: All found window widgets under the Maya window
    """
    windows = []
    from zoo.libs.maya.qt import mayaui
    for child in mayaui.getMayaWindow().children():
        # if it has a zootoolsWindow property set, use that otherwise just use the child
        w = child.property("zootoolsWindow") or child
        if isinstance(w, FramelessWindow):
            windows.append(w)

    return windows

