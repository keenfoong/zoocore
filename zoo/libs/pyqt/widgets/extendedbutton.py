from qt import QtWidgets, QtCore, QtGui

from zoo.libs import iconlib
from zoo.libs.pyqt.extended import searchablemenu
from zoo.libs.pyqt.extended.searchablemenu import action as taggedAction
from zoo.libs.utils import zlogging, colour

logger = zlogging.getLogger(__name__)


class ButtonIcons(QtWidgets.QAbstractButton):
    """Set up the icons that change on mouse over, press and release. Inherit from this class to have icons

    .. code-block:: python

        class ExtendedButton(QtWidgets.QPushButton, ButtonIcons):
        class ExtendedButton(QtWidgets.QToolButton, ButtonIcons):

    Must be placed after the button

    """
    highlightOffset = 40
    iconName = None
    iconColor = (128, 128, 128)

    buttonIcon = None
    buttonIconHover = None

    def setHighlight(self, highlight):
        self.highlightOffset = highlight

    def setIconByName(self, iconName, color=None, size=None, colorOffset=None):
        """Set up both icons in a simple function

        :param iconName:
        :param color:
        :param size:
        :param colorOffset:
        :return:
        """
        if size is not None:
            self.setIconSize(QtCore.QSize(size, size))

        if colorOffset is not None:
            self.highlightOffset = colorOffset

        color = color or self.iconColor

        self.iconName = iconName
        self.setIconColor(color, update=False)

        self.updateIcons()

    def setIconColor(self, color, update=True):
        self.iconColor = color

        if update and self.buttonIcon is not None:
            self.updateIcons()

    def updateIcons(self):
        hoverCol = colour.offsetColor(self.iconColor, self.highlightOffset)
        self.buttonIcon = iconlib.iconColorized(self.iconName, size=self.iconSize().width(), color=self.iconColor)
        self.buttonIconHover = iconlib.iconColorized(self.iconName, size=self.iconSize().width(), color=hoverCol)
        self.setIcon(self.buttonIcon)

    def setIconIdle(self, icon):
        """Set the button Icon when idle or default.

        :param icon:
        :return:
        """
        self.buttonIcon = icon
        self.setIcon(icon)

    def setIconHover(self, iconHover):
        """Set the button icon for when mouse hovers over

        :param iconHover:
        :return:
        """
        self.buttonIconHover = iconHover

    def enterEvent(self, event):
        """
        Button Hover on mouse enter

        :param event:
        :return:
        """
        if self.buttonIconHover is not None:
            self.setIcon(self.buttonIconHover)

    def leaveEvent(self, event):
        """Button Hover on mouse leave

        :param event:
        :return:
        """
        self.setIcon(self.buttonIcon)


class ExtendedButton(QtWidgets.QPushButton, ButtonIcons):
    """
    Push Button that allows you to have the left click, middle click, and right click.

    Each click allows for a menu

    .. code-block:: python

        # You can use it in a similar fashion to QPushbutton
        ExtendedButton(icon=iconlib.iconColorized("magic", size=32, color=(128,128,128)),
                       iconHover=iconlib.iconColorized("magic", size=32, color=(255,255,255)))

        # Set the hover through the constructor like above or simply set the iconName and offset

    """

    leftClicked = QtCore.Signal()
    middleClicked = QtCore.Signal()
    rightClicked = QtCore.Signal()

    leftDoubleClicked = QtCore.Signal()
    middleDoubleClicked = QtCore.Signal()
    rightDoubleClicked = QtCore.Signal()

    SINGLE_CLICK = 1
    DOUBLE_CLICK = 2

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

        # Is menu searchable?
        self.menuSearchable = {QtCore.Qt.LeftButton: False,
                               QtCore.Qt.MidButton: False,
                               QtCore.Qt.RightButton: False}

        self.menuPadding = 5

        self.menuAlign = QtCore.Qt.AlignLeft

        self.clicked.connect(lambda: self.leftClicked.emit())
        self.leftClicked.connect(lambda: self.contextMenu(QtCore.Qt.LeftButton))
        self.middleClicked.connect(lambda: self.contextMenu(QtCore.Qt.MidButton))
        self.rightClicked.connect(lambda: self.contextMenu(QtCore.Qt.RightButton))

        self.doubleClickInterval = QtWidgets.QApplication.instance().doubleClickInterval()  # 500
        self.doubleClickEnabled = doubleClickEnabled
        self.lastClick = None
        self.iconName = None
        self.highlightOffset = 40
        self.iconColor = None

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

    def setWindowTitle(self, windowTitle, mouseMenu=QtCore.Qt.LeftButton):
        """Set the window title of the menu, if it gets teared off

        :param windowTitle:
        :param mouseMenu:
        :return:
        """
        menu = self.getMenu(mouseMenu, searchable=self.isSearchable(mouseMenu))
        menu.setWindowTitle(windowTitle)

    def setTearOffEnabled(self, mouseMenu=QtCore.Qt.LeftButton, tearoff=True):
        """Set the tear off enabled

        :param mouseMenu:
        :param tearoff:
        :param windowTitle:
        :return:
        """
        menu = self.getMenu(mouseMenu, searchable=self.isSearchable(mouseMenu))
        menu.setTearOffEnabled(tearoff)

    def setMenu(self, menu, mouseButton=QtCore.Qt.LeftButton):
        """Set the menu based

        :param menu:
        :type menu: QtWidgets.QMenu
        :param mouseButton:
        :return:
        """
        self.clickMenu[mouseButton] = menu

    def setSearchable(self, mouseMenu=QtCore.Qt.LeftButton, searchable=True):
        self.menuSearchable[mouseMenu] = searchable
        # todo set searchable for existing menus

    def isSearchable(self, mouseMenu=QtCore.Qt.LeftButton):
        """Checks if the button menu is searchable or not.

        :param mouseMenu:
        :return:
        """
        if self.clickMenu[mouseMenu] is not None:
            return isinstance(self.clickMenu[mouseMenu], searchablemenu.SearchableMenu)

        return self.menuSearchable[mouseMenu]

    def setMenuAlign(self, align=QtCore.Qt.AlignLeft):
        self.menuAlign = align

    def mousePressEvent(self, event):
        """Mouse set down button visuals

        :param event:
        :return:
        """

        if not QtCore.Qt:
            return

        if event.button() == QtCore.Qt.MidButton:
            self.setDown(True)
        elif event.button() == QtCore.Qt.RightButton:
            self.setDown(True)

        self.lastClick = self.SINGLE_CLICK

    def mouseReleaseEvent(self, event):
        """Mouse release event plays the menus

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
        if self.lastClick == self.SINGLE_CLICK:
            QtCore.QTimer.singleShot(self.doubleClickInterval,
                                     lambda: self.mouseSingleClickAction(button))
        else:
            self.mouseDoubleClickAction(event.button())

    def mouseSingleClickAction(self, button):
        """The actual single click action

        :param button:
        :return:
        """

        if self.lastClick == self.SINGLE_CLICK:
            if button == QtCore.Qt.LeftButton:
                self.leftClicked.emit()
            elif button == QtCore.Qt.MidButton:
                self.middleClicked.emit()
            elif button == QtCore.Qt.RightButton:
                self.rightClicked.emit()

    def mouseDoubleClickAction(self, button):
        """The actual double click Action

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
        """
        Detects Double click event.

        :param event:
        :return:
        """
        self.lastClick = self.DOUBLE_CLICK

    def contextMenu(self, mouseButton):
        """Run context menu depending on mouse button

        :param mouseButton:
        :return:
        """
        menu = self.clickMenu[mouseButton]

        # Set focus
        if isinstance(menu, searchablemenu.SearchableMenu):
            searchEdit = menu.searchEdit
            searchEdit.setFocus()

        # Show menu
        if menu is not None and self.menuActive[mouseButton]:
            pos = self.menuPos(widget=menu, align=self.menuAlign)
            menu.exec_(pos)

    def menuPos(self, align=QtCore.Qt.AlignLeft, widget=None):
        """
        Get menu position based on the current widget position and perimeter
        :param align: Align the menu left or right
        :type align: QtCore.Qt.AlignLeft or QtCore.Qt.AlignRight
        :param widget: The widget to calculate the width based off. Normally it is the menu
        :type widget: QtWidgets.QWidget
        :return:
        """
        pos = 0

        if align == QtCore.Qt.AlignLeft:
            point = self.rect().bottomLeft() - QtCore.QPoint(0, -self.menuPadding)
            pos = self.mapToGlobal(point)
        elif align == QtCore.Qt.AlignRight:
            point = self.rect().bottomRight() - QtCore.QPoint(widget.sizeHint().width(), -self.menuPadding)
            pos = self.mapToGlobal(point)

        return pos

    def getMenu(self, mouseMenu=QtCore.Qt.LeftButton, searchable=False, autoCreate=True):
        """Get menu depending on the mouse button pressed

        :param mouseMenu:
        :return:
        """

        if self.clickMenu[mouseMenu] is None:
            if searchable and autoCreate:
                self.clickMenu[mouseMenu] = searchablemenu.SearchableMenu(objectName="extendedButton",
                                                                          title="Extended Button")
            else:
                self.clickMenu[mouseMenu] = QtWidgets.QMenu()

        return self.clickMenu[mouseMenu]

    def addAction(self, name, mouseMenu=QtCore.Qt.LeftButton, connect=None, checkable=False, action=None, icon=None):
        """Add a new menu item through an action

        :param mouseMenu: Expects QtCore.Qt.LeftButton, QtCore.Qt.MidButton, or QtCore.Qt.RightButton
        :param name: The text for the new menu item
        :param connect: The function to connect when the menu item is pressed
        :param checkable: If the menu item is checkable
        :return:
        """
        menu = self.getMenu(mouseMenu, searchable=self.isSearchable(mouseMenu))

        if action is not None:
            menu.addAction(action)
            return

        newAction = taggedAction.TaggedAction(name, parent=menu)
        newAction.setCheckable(checkable)
        newAction.tags = set(self.stringToTags(name))
        menu.addAction(newAction)

        if icon is not None:
            newAction.setIcon(icon)

        if connect is not None:
            if checkable:
                newAction.triggered.connect(lambda: connect(newAction))
            else:
                newAction.triggered.connect(connect)

        return newAction

    def addSeparator(self, mouseMenu=QtCore.Qt.LeftButton):
        """
        Add a separator in the menu
        :param mouseMenu:
        :return:
        """
        menu = self.getMenu(mouseMenu)
        menu.addSeparator()

    def stringToTags(self, string):
        """Break down string to tags so it is easily searchable

        :param string:
        :return:
        """
        ret = []
        ret += string.split(" ")
        ret += [s.lower() for s in string.split(" ")]

        return ret


