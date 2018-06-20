from qt import QtWidgets,QtCore

from zoo.libs.pyqt.widgets.extendedbutton import ExtendedButton


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
    def __init__(self, icon=None, iconHover=None, parent=None):
        super(IconMenuButton, self).__init__(icon=icon, iconHover=iconHover, parent=parent)
        self.initUi()

    def initUi(self):
        if self.leftMenu is not None:
            self.leftMenu.setToolTipsVisible(True)

        if self.middleMenu is not None:
            self.middleMenu.setToolTipsVisible(True)

        if self.rightMenu is not None:
            self.rightMenu.setToolTipsVisible(True)

    def addAction(self, name, mouseMenu=QtCore.Qt.LeftButton, connect=None, checkable=False, action=None):
        """
        Add a new menu item through an action
        :param mouseMenu: Expects QtCore.Qt.LeftButton, QtCore.Qt.MidButton, or QtCore.Qt.RightButton
        :param name: The text for the new menu item
        :param connect: The function to connect when the menu item is pressed
        :return:
        """
        menu = self.getMenu(mouseMenu)

        if action is not None:
            menu.addAction(action)
            return

        newAction = QtWidgets.QAction(name, menu, checkable=checkable)
        menu.addAction(newAction)

        if connect is not None:
            newAction.triggered.connect(connect)

    def addSeparator(self, mouseMenu=QtCore.Qt.LeftButton):
        """
        Add a separator in the menu
        :param mouseMenu:
        :return:
        """
        menu = self.getMenu(mouseMenu)
        menu.addSeparator()

    def getMenu(self, mouseMenu=QtCore.Qt.LeftButton):
        """
        Get menu depending on the mouse button pressed
        :param mouseMenu:
        :return:
        """

        menu = None

        if mouseMenu == QtCore.Qt.LeftButton:
            if self.leftMenu is None:
                self.leftMenu = QtWidgets.QMenu()
            menu = self.leftMenu
        elif mouseMenu == QtCore.Qt.MidButton:
            if self.middleMenu is None:
                self.middleMenu = QtWidgets.QMenu()
            menu = self.middleMenu
        elif mouseMenu == QtCore.Qt.RightButton:
            if self.rightMenu is None:
                self.rightMenu = QtWidgets.QMenu()
            menu = self.rightMenu

        return menu

