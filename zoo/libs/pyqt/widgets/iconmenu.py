from qt import QtWidgets,QtCore

from zoo.libs.pyqt.widgets.extendedbutton import ExtendedButton

class IconMenuButton(ExtendedButton):
    def __init__(self, icon, parent, leftClickMenu=None, middleClickMenu=None, rightClickMenu=None):
        super(IconMenuButton, self).__init__(icon, parent, leftClickMenu, middleClickMenu, rightClickMenu)
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

        
    

