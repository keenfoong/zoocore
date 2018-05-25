from qt import QtWidgets, QtCore, QtGui

from zoo.libs import iconlib
from zoo.libs.maya.qt import mayaui
from zoo.libs.pyqt.widgets import flowlayout, iconmenu


class FlowToolBar(QtWidgets.QWidget):
    """
    A tool bar based off the FlowLayout. The buttons will flow from left to right and wrap to
    the next row if there is no space
    """

    def __init__(self, parent=None):
        super(FlowToolBar, self).__init__(parent)
        self.artistUi = parent
        self.mainLayout = flowlayout.FlowLayout(margin=0, spacing=1)
        self.setLayout(self.mainLayout)
        self.iconSize = 22
        self.iconPadding = 2
        self.menuIndicatorIcon = "arrowmenu"

        self.initUi()

    def initUi(self):
        """
        Overridden by subclass
        :return:
        """
        pass

    def addTool(self, iconName, name, iconColor=(255,255,255)):
        """
        Creates a new tool button based on the icon name, and the name.
        :param iconName: Name of the icon to retrieve
        :param name: Name of the tool
        :return:
        """
        # Create an item with a caption
        btn = QtWidgets.QPushButton(iconlib.iconColorized(iconName, mayaui.dpiScale(self.iconSize), color=iconColor), "")
        btn.setProperty("name", name)
        btn.setIconSize(mayaui.sizeByDpi(QtCore.QSize(self.iconSize + self.iconPadding,
                                                      self.iconSize + self.iconPadding)))
        btn.clicked.connect(self.toolsClicked)

        self.mainLayout.addWidget(btn)
        return btn

    def addToolMenu(self, iconName, name, actions, iconColor=(255,255,255), showIndicator=True):
        """
        Adds a new tool menu.
        :param iconName: Name of the icon to retrieve
        :param name: Name of the tool
        :param actions: Actions is a list of tuples with the name and function to run
        eg ('Name', self.menuItemPressed)
        :return:
        """
        overlayName = None
        if showIndicator:
            overlayName = self.menuIndicatorIcon

        btn = iconmenu.IconMenuButton(iconlib.iconColorized(iconName, size=mayaui.dpiScale(self.iconSize), color=iconColor, overlayName=overlayName))
        btn.setProperty("name", name)
        btn.setIconSize(mayaui.sizeByDpi(QtCore.QSize(self.iconSize + self.iconPadding,
                                                      self.iconSize + self.iconPadding)))
        btn.clicked.connect(self.toolsClicked)

        for a in actions:
            btn.addAction(a[0], a[1])

        self.mainLayout.addWidget(btn)
        return btn

    def clear(self):
        """
        Clear all widgets
        :return:
        """
        self.mainLayout.clear()

    def toolsClicked(self):
        """
        All buttons will run through here. It will then run a separate function telling which
        button was pressed, along with some other details

        :return:
        """
        data = self.sender().property("name")
        self.buttonClicked(self.sender(), data)

    def buttonClicked(self, wgt, name):
        """
        Overridden by the subclass
        :param wgt: The widget that was pressed, typically a button
        :param name: The name of the tool
        :return:
        """
        pass

    def setHeight(self, height):
        self.setFixedHeight(height)


