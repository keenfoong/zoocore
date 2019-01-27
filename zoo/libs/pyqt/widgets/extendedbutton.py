from functools import partial

from qt import QtWidgets, QtCore, QtGui

from zoo.libs import iconlib
from zoo.libs.pyqt import utils, uiconstants
from zoo.libs.pyqt.extended import searchablemenu, expandedtooltip
from zoo.libs.pyqt.extended.searchablemenu import action as taggedAction
from zoo.libs.utils import zlogging

logger = zlogging.getLogger(__name__)

BTN_DEFAULT = uiconstants.BTN_DEFAULT
BTN_TRANSPARENT_BG = uiconstants.BTN_TRANSPARENT_BG

class ButtonIcons(QtWidgets.QAbstractButton):
    """Set up the icons that change on mouse over, press and release. Inherit from this class to have icons

    .. code-block:: python

        class ExtendedButton(QtWidgets.QPushButton, ButtonIcons):
        class ExtendedButton(QtWidgets.QToolButton, ButtonIcons):

    Must be placed after the button.

    """
    highlightOffset = 40
    iconNames = None
    iconColors = (128, 128, 128)
    iconScaling = []

    buttonIcon = None
    buttonIconPressed = None
    buttonIconHover = None

    def setHighlight(self, highlight):
        self.highlightOffset = highlight

    def setIconByName(self, iconNames, colors=None, size=None, colorOffset=None, iconScaling=None):
        """Set up both icons in a simple function

        :param iconNames: name of the icon
        :type iconNames: basestring or list
        :param colors: the icon regular color
        :type colors: tuple or list or None
        :param size: Size is dpiScaled automatically here, but can be passed in
        :type size: int
        :param colorOffset: the amount of tint white highlight that's added when mouse over hover 0-255
        :type colorOffset: int
        :param iconScaling: the icon's scale
        :type iconScaling: int
        """
        if size is not None:
            self.setIconSize(QtCore.QSize(size, size))

        if colorOffset is not None:
            self.highlightOffset = colorOffset

        if iconScaling is not None:
            self.iconScaling = iconScaling
        colors = colors or self.iconColors

        self.iconNames = iconNames
        self.setIconColor(colors, update=False)
        self.updateIcons()

    def setIconColor(self, colors, update=True):
        self.iconColors = colors
        if update and self.buttonIcon is not None and self.iconNames is not None:
            self.updateIcons()

    def updateIcons(self):
        if self.iconNames is None or self.iconNames == []:
            # Icon name is none? should mean the button is not ready yet
            return

        hoverCol = (255, 255, 255, self.highlightOffset)

        self.buttonIcon = iconlib.iconColorizedLayered(self.iconNames,
                                                       size=self.iconSize().width(),
                                                       iconScaling=self.iconScaling,
                                                       colors=self.iconColors)
        self.buttonIconHover = iconlib.iconColorizedLayered(self.iconNames,
                                                            size=self.iconSize().width(),
                                                            colors=self.iconColors,
                                                            iconScaling=self.iconScaling,
                                                            tintColor=hoverCol)

        self.setIcon(self.buttonIcon)

    def setIconSize(self, size):
        """ Set icon size

        :param size:
        :return:
        """
        if self.iconNames is None:
            return

        super(ButtonIcons, self).setIconSize(utils.sizeByDpi(size))
        self.updateIcons()

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
        """Button Hover on mouse enter

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
        if self.buttonIcon is not None:
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
    clicked = leftClicked

    SINGLE_CLICK = 1
    DOUBLE_CLICK = 2

    highlightOffset = 40

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

        self.leftClicked.connect(partial(self.contextMenu, QtCore.Qt.LeftButton))
        self.middleClicked.connect(partial(self.contextMenu, QtCore.Qt.MidButton))
        self.rightClicked.connect(partial(self.contextMenu, QtCore.Qt.RightButton))

        self.doubleClickInterval = QtWidgets.QApplication.instance().doubleClickInterval()  # 500
        self.doubleClickEnabled = doubleClickEnabled
        self.lastClick = None
        self.iconName = None
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
        """ Sets the menu based on mouse button

        :param menu:
        :type menu: QtWidgets.QMenu
        :param mouseButton:
        :return:
        """
        self.clickMenu[mouseButton] = menu

    def setFixedSize(self, size):
        """ Sets fixed size

        :param size: Dpiscaling is automatically applied here
        :return:
        """
        return super(ExtendedButton, self).setFixedSize(utils.dpiScale(size))

    def setFixedHeight(self, height):
        """ DpiScaling version of set fixed height

        :param height:
        :return:
        """
        return super(ExtendedButton, self).setFixedHeight(utils.dpiScale(height))

    def setFixedWidth(self, width):
        """ DpiScaling version of set fixed width

        :param width:
        :return:
        """
        return super(ExtendedButton, self).setFixedWidth(utils.dpiScale(width))

    def setSearchable(self, mouseMenu=QtCore.Qt.LeftButton, searchable=True):
        self.menuSearchable[mouseMenu] = searchable

        if self.clickMenu[mouseMenu] is not None:
            self.clickMenu[mouseMenu].setSearchVisibility(searchable)

    def isSearchable(self, mouseMenu=QtCore.Qt.LeftButton):
        """ Checks if the button menu is searchable or not.

        :param mouseMenu:
        :return:
        """
        if self.clickMenu[mouseMenu] is not None:
            return self.clickMenu[mouseMenu].searchVisible()

        return self.menuSearchable[mouseMenu]

    def setMenuAlign(self, align=QtCore.Qt.AlignLeft):
        self.menuAlign = align

    def clearMenu(self, mouseMenu):
        """Clears specified menu

        :param mouseMenu: QtCore.Qt.LeftButton, QtCore.Qt.MidButton, QtCore.Qt.RightButton
        :return:
        """

        if self.clickMenu[mouseMenu] is not None:
            self.clickMenu[mouseMenu].clear()

    def mousePressEvent(self, event):
        """ Mouse set down button visuals

        :param event:
        :return:
        """
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

        if self.lastClick == self.SINGLE_CLICK or self.doubleClickEnabled is False:
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

        # Show menu
        if menu is not None and self.menuActive[mouseButton]:
            menu.searchEdit.setFocus()

            pos = self.menuPos(widget=menu, align=self.menuAlign)
            menu.exec_(pos)

    def menuPos(self, align=QtCore.Qt.AlignLeft, widget=None):
        """Get menu position based on the current widget position and perimeter

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
        :return: The requested menu
        :rtype: QtWidgets.QMenu
        """

        if self.clickMenu[mouseMenu] is None and autoCreate:
            self.clickMenu[mouseMenu] = ExtendedButtonMenu(objectName="extendedButton", title="Extended Button")
            if not searchable:
                self.clickMenu[mouseMenu].setSearchVisible(False)

        return self.clickMenu[mouseMenu]

    def addAction(self, name, mouseMenu=QtCore.Qt.LeftButton,
                  connect=None, checkable=False,
                  checked=True, action=None, icon=None):
        """Add a new menu item through an action

        :param mouseMenu: Expects QtCore.Qt.LeftButton, QtCore.Qt.MidButton, or QtCore.Qt.RightButton
        :param name: The text for the new menu item
        :param connect: The function to connect when the menu item is pressed
        :param checkable: If the menu item is checkable
        :return:
        :rtype: taggedAction.TaggedAction

        """
        # temporarily disabled isSearchable due to c++ error
        menu = self.getMenu(mouseMenu, searchable=False)#self.isSearchable(mouseMenu))

        if action is not None:
            menu.addAction(action)
            return

        newAction = taggedAction.TaggedAction(name, parent=menu)
        newAction.setCheckable(checkable)
        newAction.setChecked(checked)
        newAction.tags = set(self.stringToTags(name))
        menu.addAction(newAction)

        if icon is not None:
            newAction.setIcon(icon)

        if connect is not None:
            if checkable:
                newAction.triggered.connect(partial(connect, newAction))
            else:
                newAction.triggered.connect(connect)

        return newAction

    def addSeparator(self, mouseMenu=QtCore.Qt.LeftButton):
        """ Add a separator in the menu

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


class ExtendedPushButton(ExtendedButton):

    def __init__(self, *args, **kwargs):
        """ Same as ExtendedButton except with the default style

        :param args:
        :param kwargs:
        """
        super(ExtendedPushButton, self).__init__(*args, **kwargs)
        utils.setStylesheetObjectName(self, "DefaultButton")


class ExtendedButtonMenu(searchablemenu.SearchableMenu):
    def __init__(self, *args, **kwargs):
        super(ExtendedButtonMenu, self).__init__(*args, **kwargs)
        self.ttKeyPressed = False
        self.ttKey = QtCore.Qt.Key_Control

    def keyPressEvent(self, event):
        """ Key press event

        :param event:
        :return:
        """

        # Use expanded tooltips if it has any
        if event.key() == self.ttKey:
            pos = self.mapFromGlobal(QtGui.QCursor.pos())
            action = self.actionAt(pos)
            if expandedtooltip.hasExpandedTooltips(action):
                self._popuptooltip = expandedtooltip.ExpandedTooltipPopup(action, iconSize=utils.dpiScale(40),
                                                                          popupRelease=self.ttKey)
            self.ttKeyPressed = True

        super(ExtendedButtonMenu, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.ttKeyPressed = False


def BtnTransparentBG(**kwargs):
    """Create a button with a transparent bg.  Saves code from doing this over and over
    Default Icon colour (None) is light grey and turns white (lighter in color) with mouse over.

    :Note: WIP, Will fill out more options with time

    :param kwargs: See the doc string from the function BtnStyle
    :type kwargs: dict
    :return qtBtn: returns a qt button widget
    :rtype qtBtn: object
    """
    parent = kwargs.get("parent")
    text = kwargs.get("text")
    icon = kwargs.get("icon", (255, 255, 255))
    toolTip = kwargs.get("toolTip", "")
    iconColor = kwargs.get("iconColor")
    minWidth = kwargs.get("minWidth")
    maxWidth = kwargs.get("maxWidth")
    minHeight = kwargs.get("maxHeight")
    maxHeight = kwargs.get("maxHeight")

    btn = ExtendedButton(parent=parent, text=text)
    if icon:
        btn.setIconByName(icon, colors=iconColor)
        """ todo: icon colorized anti aliasing is not working correctly?  Icons appear thicker
        # will want this code later
        self.setIcon(iconlib.iconColorized(icon, size=iconSize, color=iconColor, overlayName=overlayIconName,
                           overlayColor=overlayIconColor))
        """
    btn.setToolTip(toolTip)
    if minWidth is not None:
        btn.setMinimumWidth(utils.dpiScale(minWidth))
    if maxWidth is not None:
        btn.setMaximumWidth(utils.dpiScale(maxWidth))
    if minHeight is not None:
        btn.setMinimumHeight(utils.dpiScale(minHeight))
    if maxHeight is not None:
        btn.setMaximumHeight(utils.dpiScale(maxHeight))
    return btn


def BtnRegular(**kwargs):
    """Creates regular pyside button with text or an icon.

    :note: Will fill out more options with time.
    :note: Should probably override ExtendedButton and not QtWidgets.QPushButton for full options.

    :param kwargs: See the doc string from the function BtnStyle
    :type kwargs: dict
    :return qtBtn: returns a qt button widget
    :rtype qtBtn: object
    """
    parent = kwargs.get("parent")
    text = kwargs.get("text")
    icon = kwargs.get("icon", (255, 255, 255))
    toolTip = kwargs.get("toolTip", "")
    iconSize = kwargs.get("iconSize")
    minWidth = kwargs.get("minWidth")
    maxWidth = kwargs.get("maxWidth")
    minHeight = kwargs.get("maxHeight")
    maxHeight = kwargs.get("maxHeight")

    btn = QtWidgets.QPushButton(text, parent=parent)
    if icon:
        btn.setIcon(iconlib.icon(icon))
        btn.setIconSize(QtCore.QSize(iconSize, iconSize))
        """ todo: icon colorized anti aliasing is not working correctly?  Icons appear thicker
        self.setIcon(iconlib.iconColorized(icon, size=iconSize, color=iconColor, overlayName=overlayIconName,
                           overlayColor=overlayIconColor))
        """
    btn.setToolTip(toolTip)
    if minWidth is not None:
        btn.setMinimumWidth(utils.dpiScale(minWidth))
    if maxWidth is not None:
        btn.setMaximumWidth(utils.dpiScale(maxWidth))
    if minHeight is not None:
        btn.setMinimumHeight(utils.dpiScale(minHeight))
    if maxHeight is not None:
        btn.setMaximumHeight(utils.dpiScale(maxHeight))
    # todo: button height padding should be set in the prefs stylesheet
    padWidth = utils.dpiScale(3)
    padHeight = utils.dpiScale(4)
    padding = "{0} {1} {0} {1}".format(padHeight, padWidth)
    btn.setStyleSheet("QPushButton {padding: " + padding + ";}")
    return btn


def buttonStyle(text=None, icon=None, parent=None, toolTip="", textCaps=False,
                iconColor=(255, 255, 255), minWidth=None, maxWidth=None, iconSize=16, overlayIconName=None,
                overlayIconColor=None, minHeight=None, maxHeight=None, style=BTN_DEFAULT):
    """ Create a button with text or an icon in various styles and options.

    Style - 0 - BTN_DEFAULT - Default pyside button with optional text or an icon.
    Style - 1 - BTN_TRANSPARENT_BG - Default pyside button w transparent bg. Icon colour is grey and lighter with hover.

    :param text: The button text.
    :type icon: str
    :param icon: The icon image name, icon is automatically sized.
    :type icon: str
    :param parent: The parent widget.
    :type parent: object
    :param toolTip: The tooltip as seen with mouse over extra information.
    :type toolTip: str
    :param style: The style of the button, 0 default, 1 no bg. See pyside.uiconstants BTN_DEFAULT, BTN_TRANSPARENT_BG.
    :type style: int
    :param textCaps: Bool to make the button text all caps.
    :type textCaps: bool
    :param iconColor: The color of the icon (255, 134, 23) :note: Not implemented yet.
    :type iconColor: tuple
    :param minWidth: minimum width of the button in pixels, DPI handled.
    :type minWidth: int
    :param maxWidth: maximum width of the button in pixels, DPI handled.
    :type maxWidth: int
    :param iconSize: The size of the icon in pixels, always square, DPI handled.
    :type iconSize: int
    :param overlayIconName: The name of the icon image that will be overlayed on top of the original icon.
    :param overlayIconName: tuple
    :param overlayIconColor: The color of the overlay image icon (255, 134, 23) :note: Not implemented yet.
    :type overlayIconColor: tuple
    :param minHeight: minimum height of the button in pixels, DPI handled.
    :type minHeight: int
    :param maxHeight: maximum height of the button in pixels, DPI handled.
    :type maxHeight: int
    :return qtBtn: returns a qt button widget.
    :rtype qtBtn: object
    """
    if style == BTN_DEFAULT:
        return BtnRegular(text=text, icon=icon, parent=parent, toolTip=toolTip, textCaps=textCaps,
                          iconColor=iconColor, minWidth=minWidth, maxWidth=maxWidth, iconSize=iconSize,
                          overlayIconName=overlayIconName, overlayIconColor=overlayIconColor, minHeight=minHeight,
                          maxHeight=maxHeight)
    if style == BTN_TRANSPARENT_BG:
        return BtnTransparentBG(text=text, icon=icon, parent=parent, toolTip=toolTip, textCaps=textCaps,
                                iconColor=iconColor, minWidth=minWidth, maxWidth=maxWidth, iconSize=iconSize,
                                overlayIconName=overlayIconName, overlayIconColor=overlayIconColor, minHeight=minHeight,
                                maxHeight=maxHeight)

