from qt import QtWidgets, QtCore, QtGui


class IconMenuButton(QtWidgets.QPushButton):
    """
    A Push button that fires a menu underneath it
    """
    def __init__(self, icon):
        super(IconMenuButton, self).__init__(icon, "")
        self.menu = QtWidgets.QMenu()

        self.initUi()
        self.connections()
        self.menuHidden = True

    def connections(self):
        """
        Connections for the Icon menu
        :return:
        """
        self.clicked.connect(self.contextMenu)
        self.menu.aboutToHide.connect(self.hidden)

    def addAction(self, name, connect=None):
        """
        Add a new menu item through an action
        :param name: The text for the new menu item
        :param connect: The function to connect when the menu item is pressed
        :return:
        """
        newAction = QtWidgets.QAction(name, self.menu)
        self.menu.addAction(newAction)

        if connect is not None:
            newAction.triggered.connect(connect)

    def initUi(self):
        """
        Icon Menu settings
        :return:
        """
        self.menu.setToolTipsVisible(True)

    def hidden(self):
        self.menuHidden = True

    def contextMenu(self):
        """
        Display the context menu
        :return:
        """
        self.menu.exec_(self.menuPos())

    def menuPos(self):
        """
        Get menu position based on the current widget position and perimeter
        :return:
        """
        point = self.rect().bottomLeft()
        return self.mapToGlobal(point)
