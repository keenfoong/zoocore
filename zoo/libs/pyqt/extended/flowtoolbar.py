from qt import QtWidgets, QtCore, QtGui

from zoo.libs import iconlib
from zoo.libs.pyqt.widgets import flowlayout, iconmenu
from zoo.libs.utils import colour


class FlowToolBar(QtWidgets.QWidget):
    """
    A tool bar based off the FlowLayout. The buttons will flow from left to right and wrap to
    the next row if there is no space

    ::example:
    >>> flowToolbar = FlowToolBar()
    >>> flowToolbar.addTool("stream2", name="Tool Button Name", iconColor=(255,255,255))
    >>> flowToolbar.addToolMenu("stream2", name="Tool Button Name", actions=[('Menu Item 1', func1),('Menu Item 2', func2)])
    >>>
    >>> def func1():
    >>>     pass
    >>> def func2():
    >>>     pass

    """

    def __init__(self, parent=None, menuIndicatorIcon="arrowmenu"):
        super(FlowToolBar, self).__init__(parent)
        self.artistUi = parent
        self.mainLayout = flowlayout.FlowLayout(margin=0, spacing=1)
        self.setLayout(self.mainLayout)
        self.iconSize = 22
        self.iconPadding = 2
        self.menuIndicatorIcon = menuIndicatorIcon

        self.initUi()

    def initUi(self):
        """
        Overridden by subclass
        :return:
        """
        pass

    def setIconSize(self, size):
        """
        Set the size of the icons of the tools and toolmenus
        :param size:
        :return:
        """
        self.iconSize = size

        # Set the icon size, possibly will need to get them to get a new icon through iconColorized
        for i in range(0, self.mainLayout.count()):
            widget = self.mainLayout.itemAt(i).widget()
            widget.setIconSize(self.getIconSize())

    def setIconPadding(self, padding):
        """
        Sets the padding for the icons of the tools and the tool menus
        :param padding:
        :return:
        """
        self.iconPadding = padding

    def addTool(self, iconName, name, iconColor=(255, 255, 255), doubleClickEnabled=False):
        """
        Creates a new tool button based on the icon name, and the name.
        :param iconName: Name of the icon to retrieve
        :param name: Name of the tool
        :param iconColor: Color of the icon for the tool
        :param doubleClickEnabled: Enable doubleclick for button
        :return:
        """
        # Create an item with a caption

        btn = iconmenu.IconMenuButton(icon=iconlib.iconColorized(iconName, size=self.iconSize, color=iconColor),
                                      iconHover=iconlib.iconColorized(iconName,
                                                                      size=self.iconSize,
                                                                      color=colour.offsetColor(iconColor, 40)),
                                      parent=self)

        btn.setDoubleClickEnabled(doubleClickEnabled)
        btn.setDoubleClickInterval(150)
        btn.setProperty("name", name)
        btn.setIconSize(self.getIconSize())
        btn.leftClicked.connect(self.toolsClicked)

        self.mainLayout.addWidget(btn)
        return btn

    def getIconSize(self):
        """
        Returns the icon generated QSize
        :return:
        """
        return QtCore.QSize(self.iconSize + self.iconPadding,
                            self.iconSize + self.iconPadding)

    def addToolMenu(self, iconName, name, actions, iconColor=(255, 255, 255), showIndicator=True):
        """
        Adds a new tool menu.
        :param iconName: Name of the icon to retrieve
        :param name: Name of the tool
        :param actions: Actions is a list of tuples with the name and function to run
        eg ('Name', self.menuItemPressed)
        :param iconColor: The icon color
        :param showIndicator: Show the menu indicator (the arrow in the corner)
        :return:
        """
        overlayName = None
        if showIndicator:
            overlayName = self.menuIndicatorIcon

        btn = iconmenu.IconMenuButton(icon=iconlib.iconColorized(iconName,
                                                                 size=self.iconSize,
                                                                 color=iconColor,
                                                                 overlayName=overlayName),
                                      iconHover=iconlib.iconColorized(iconName,
                                                                      size=self.iconSize,
                                                                      color=colour.offsetColor(iconColor, 80),
                                                                      overlayName=overlayName),
                                      parent=self)
        btn.setProperty("name", name)
        btn.setIconSize(QtCore.QSize(self.iconSize + self.iconPadding,
                                     self.iconSize + self.iconPadding))
        btn.leftClicked.connect(self.toolsClicked)

        for a in actions:
            btn.addAction(a[0], connect=a[1])

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

