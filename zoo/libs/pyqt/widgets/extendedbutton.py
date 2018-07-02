from qt import QtWidgets, QtCore

from zoo.libs import iconlib


class ExtendedButton(QtWidgets.QPushButton):
    """
    Push Button that allows you to have the left click, middle click, and right click.

    Each click allows for a menu

    :example:
    You can use it in a similar fashion to QPushbutton
    >>> ExtendedButton(icon=iconlib.iconColorized("magic", size=32, color=(255,255,255)))

    """

    leftClicked = QtCore.Signal()
    middleClicked = QtCore.Signal()
    rightClicked = QtCore.Signal()

    leftDoubleClicked = QtCore.Signal()
    middleDoubleClicked = QtCore.Signal()
    rightDoubleClicked = QtCore.Signal()

    def __init__(self, icon=None, iconHover=None,
                 text=None, parent=None,
                 doubleClickEnabled=False):

        self.buttonIcon = icon
        self.buttonIconHover = iconHover

        super(ExtendedButton, self).__init__(icon=self.buttonIcon, text=text, parent=parent)

        # To check of the menu is active
        self.menuActive = {QtCore.Qt.LeftButton: True,
                           QtCore.Qt.MidButton: True,
                           QtCore.Qt.RightButton: True}

        # Store menus into a dictionary
        self.clickMenu = {QtCore.Qt.LeftButton: None,
                          QtCore.Qt.MidButton: None,
                          QtCore.Qt.RightButton: None}

        self.menuPadding = 5

        self.menuAlign = QtCore.Qt.AlignLeft

        self.clicked.connect(lambda: self.leftClicked.emit())
        self.leftClicked.connect(lambda: self.contextMenu(QtCore.Qt.LeftButton))
        self.middleClicked.connect(lambda: self.contextMenu(QtCore.Qt.MidButton))
        self.rightClicked.connect(lambda: self.contextMenu(QtCore.Qt.RightButton))

        self.doubleClickInterval = QtWidgets.QApplication.instance().doubleClickInterval()  # 500
        self.doubleClickEnabled = doubleClickEnabled
        self.lastClick = None

    def setDoubleClickInterval(self, interval=150):
        """
        Sets the interval of the double click, defaults to 150
        :param interval:
        :return:
        """
        self.doubleClickInterval = interval

    def setDoubleClickEnabled(self, enabled):
        """
        Enables double click signals for this widget
        :param enabled:
        :return:
        """
        self.doubleClickEnabled = enabled

    def setMenu(self, menu, mouseButton=QtCore.Qt.LeftButton):
        """
        Set the menu based
        :param menu:
        :type menu: QtWidgets.QMenu
        :param mouseButton:
        :return:
        """
        self.clickMenu[mouseButton] = menu

    def setMenuAlign(self, align=QtCore.Qt.AlignLeft):
        self.menuAlign = align

    def mousePressEvent(self, event):
        """
        Mouse set down button visuals
        :param event:
        :return:
        """

        if not QtCore.Qt:
            return

        if event.button() == QtCore.Qt.MidButton:
            self.setDown(True)
        elif event.button() == QtCore.Qt.RightButton:
            self.setDown(True)

        self.lastClick = "Click"

    def mouseReleaseEvent(self, event):
        """
        Mouse release event plays the menus
        :param event:
        :return:
        """
        button = event.button()
        self.setDown(False)

        # Single Clicks Only
        if not self.doubleClickEnabled:
            self.mouseSingleClickAction(button)
            return

        # Double clicks
        if self.lastClick == "Click":
            QtCore.QTimer.singleShot(self.doubleClickInterval,
                                     lambda: self.mouseSingleClickAction(button))
        else:
            self.mouseDoubleClickAction(event.button())

    def mouseSingleClickAction(self, button):
        """
        The actual single click action
        :param button:
        :return:
        """

        if self.lastClick == "Click":
            if button == QtCore.Qt.LeftButton:
                self.leftClicked.emit()
            elif button == QtCore.Qt.MidButton:
                self.middleClicked.emit()
            elif button == QtCore.Qt.RightButton:
                self.rightClicked.emit()

    def mouseDoubleClickAction(self, button):
        """
        The actual double click Action
        :param button:
        :return:
        """
        if button == QtCore.Qt.LeftButton:
            self.leftDoubleClicked.emit()
        elif button == QtCore.Qt.MidButton:
            self.middleDoubleClicked.emit()
        elif button == QtCore.Qt.RightButton:
            self.rightDoubleClicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.lastClick = "Double Click"

    def enterEvent(self, event):
        """
        Button Hover on mouse enter
        :param event:
        :return:
        """
        if self.buttonIconHover is not None:
            self.setIcon(self.buttonIconHover)

    def leaveEvent(self, event):
        """
        Button Hover on mouse leave
        :param event:
        :return:
        """
        self.setIcon(self.buttonIcon)

    def contextMenu(self, mouseButton):
        """
        Run context menu depending on mouse button
        :param mouseButton:
        :return:
        """
        menu = self.clickMenu[mouseButton]
        if menu is not None and self.menuActive[mouseButton]:
            pos = self.menuPos(menu=menu, align=self.menuAlign)
            menu.exec_(pos)

    def menuPos(self, align=QtCore.Qt.AlignLeft, menu=None):
        """
        Get menu position based on the current widget position and perimeter
        :return:
        """
        pos = 0
        if align == QtCore.Qt.AlignLeft:
            point = self.rect().bottomLeft() - QtCore.QPoint(0, -self.menuPadding)
            pos = self.mapToGlobal(point)
        elif align == QtCore.Qt.AlignRight:
            point = self.rect().bottomRight() - QtCore.QPoint(menu.sizeHint().width(), -self.menuPadding)
            pos = self.mapToGlobal(point)

        return pos

