from qt import QtWidgets,QtCore

from zoo.libs.pyqt.extended import searchablemenu
from zoo.libs.pyqt.widgets.extendedbutton import ExtendedButton
from zoo.libs.pyqt.extended.searchablemenu import action as taggedAction

class IconMenuButton(ExtendedButton):
    """
    IconMenuButton is a button that only takes an icon. Clicking it will pop up a context menu.
    Left click, middle click and right click can be customized and added with addAction

    :example:
    >>> logoButton = IconMenuButton(iconlib.icon("magic", size=32))
    >>> logoButton.setIconSize(QtCore.QSize(24, 24))

    Add to menu. The menu is automatically created if there is none and placed into
    self.leftMenu, self.middleMenu or self.rightMenu
    >>> logoButton.addAction("Create 3D Characters")
    >>> logoButton.addSeparator()
    >>> logoButton.addAction("Toggle Toolbars", connect=self.toggleContents)

    Middle Click and right click menu
    >>> logoButton.addAction("Middle Click Menu", mouseMenu=QtCore.Qt.MidButton)
    >>> logoButton.addAction("Right Click Menu", mouseMenu=QtCore.Qt.RightButton)

    """
    def __init__(self, icon=None, iconHover=None, parent=None, doubleClickEnabled=False):
        super(IconMenuButton, self).__init__(icon=icon, iconHover=iconHover, parent=parent,
                                             doubleClickEnabled=doubleClickEnabled)
        self.initUi()
        self.leftSearchable = False
        self.midSearchable = False
        self.rightSearchable = False

    def initUi(self):
        if self.leftMenu is not None:
            self.leftMenu.setToolTipsVisible(True)

        if self.middleMenu is not None:
            self.middleMenu.setToolTipsVisible(True)

        if self.rightMenu is not None:
            self.rightMenu.setToolTipsVisible(True)

    def setSearchable(self, mouseMenu=QtCore.Qt.LeftButton, searchable=True):
        if mouseMenu == QtCore.Qt.LeftButton:
            self.leftSearchable = searchable
        if mouseMenu == QtCore.Qt.MidButton:
            self.midSearchable = searchable
        if mouseMenu == QtCore.Qt.RightButton:
            self.rightSearchable = searchable
        # todo set searchable for existing menus

    def setTearOffEnabled(self, mouseMenu=QtCore.Qt.LeftButton, tearoff=True):
        self.getMenu(mouseMenu, searchable=self.isSearchable(mouseMenu)).setTearOffEnabled(tearoff)

    def isSearchable(self, mouseMenu=QtCore.Qt.LeftButton):
        if mouseMenu == QtCore.Qt.LeftButton:
            if self.leftMenu is not None:
                return isinstance(self.leftMenu, searchablemenu.SearchableMenu)
            else:
                return self.leftSearchable

        elif mouseMenu == QtCore.Qt.MidButton:
            if self.middleMenu is not None:
                return isinstance(self.middleMenu, searchablemenu.SearchableMenu)
            else:
                return self.midSearchable

        elif mouseMenu == QtCore.Qt.RightButton:
            if self.rightMenu is not None:
                return isinstance(self.rightMenu, searchablemenu.SearchableMenu)
            else:
                return self.rightSearchable

    def addAction(self, name, mouseMenu=QtCore.Qt.LeftButton, connect=None, checkable=False, action=None):
        """
        Add a new menu item through an action
        :param mouseMenu: Expects QtCore.Qt.LeftButton, QtCore.Qt.MidButton, or QtCore.Qt.RightButton
        :param name: The text for the new menu item
        :param connect: The function to connect when the menu item is pressed
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

        if connect is not None:
            if checkable:
                newAction.triggered.connect(lambda: connect(checkable))
            else:
                newAction.triggered.connect(connect)

    def stringToTags(self, string):
        """
        Break down string to tags so it is easily searchable
        :param string:
        :return:
        """
        ret = []
        ret += string.split(" ")
        ret += [s.lower() for s in string.split(" ")]

        return ret

    def addSeparator(self, mouseMenu=QtCore.Qt.LeftButton):
        """
        Add a separator in the menu
        :param mouseMenu:
        :return:
        """
        menu = self.getMenu(mouseMenu)
        menu.addSeparator()

    def getMenu(self, mouseMenu=QtCore.Qt.LeftButton, searchable=False, autoCreate=True):
        """
        Get menu depending on the mouse button pressed
        :param mouseMenu:
        :return:
        """

        menu = None

        # too many if statements, need to fix
        if mouseMenu == QtCore.Qt.LeftButton:
            if self.leftMenu is None:
                if searchable and autoCreate:
                    self.leftMenu = searchablemenu.SearchableMenu(objectName="test", title="test menu")
                else:
                    self.leftMenu = QtWidgets.QMenu()

            menu = self.leftMenu
        elif mouseMenu == QtCore.Qt.MidButton:
            if self.middleMenu is None:
                if searchable and autoCreate:
                    self.middleMenu = searchablemenu.SearchableMenu(objectName="test", title="test menu")
                else:
                    self.middleMenu = QtWidgets.QMenu()
            menu = self.middleMenu
        elif mouseMenu == QtCore.Qt.RightButton:
            if self.rightMenu is None:
                if searchable and autoCreate:
                    self.rightMenu = searchablemenu.SearchableMenu(objectName="test", title="test menu")
                else:
                    self.rightMenu = QtWidgets.QMenu()
            menu = self.rightMenu

        return menu

