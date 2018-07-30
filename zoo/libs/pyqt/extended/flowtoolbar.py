from qt import QtWidgets, QtCore, QtGui

from zoo.libs import iconlib
from zoo.libs.pyqt import utils
from zoo.libs.pyqt.widgets import flowlayout, iconmenu, dialog
from zoo.libs.utils import colour


class FlowToolBar(QtWidgets.QWidget):
    """
    A tool bar based off the FlowLayout. The buttons will flow from left to right and wrap to
    the next row if there is no space

    .. code-block:: python

        flowToolbar = FlowToolBar()
        flowToolbar.addTool("stream2", name="Tool Button Name", iconColor=(255,255,255))
        flowToolbar.addToolMenu("stream2", name="Tool Button Name", actions=[('Menu Item 1', func1),('Menu Item 2', func2)])
        def func1():
            pass
        def func2():
            pass

    """

    def __init__(self, parent=None, menuIndicatorIcon="arrowmenu"):
        super(FlowToolBar, self).__init__(parent)
        self.artistUi = parent
        self.mainLayout = utils.hBoxLayout(self)

        self.flowLayout = flowlayout.FlowLayout(margin=0, spacingX=utils.dpiScale(1), spacingY=utils.dpiScale(1))
        self.mainLayout.addLayout(self.flowLayout)
        self.setLayout(self.mainLayout)
        self.iconSize = 20
        self.iconPadding = 2
        self.menuIndicatorIcon = menuIndicatorIcon

        self.overflowMenu = False
        self.overflowMenuBtn = None


        self.overflowMenuDlg = FlowToolbarMenu(self)
        #self.dialogWidget.setStyleSheet(self.styleSheet())
        self.overflowLayout = self.overflowMenuDlg.layout()


        self.initUi()

    def initUi(self):
        """
        Overridden by subclass
        """

        self.overflowMenuBtn = self.setupOverflowMenu()


        #self.flowLayout.addWidget(self.overflowMenuBtn)


    def setIconSize(self, size):
        """Set the size of the icons of the tools and toolmenus

        :param size:
        """
        self.iconSize = size

        # Set the icon size, possibly will need to get them to get a new icon through iconColorized
        for i in range(0, self.flowLayout.count()):
            widget = self.flowLayout.itemAt(i).widget()
            widget.setIconSize(self.getIconSize())

        self.overflowMenuBtn = self.setupOverflowMenu(self.overflowMenuBtn)

    def setIconPadding(self, padding):
        """Sets the padding for the icons of the tools and the tool menus

        :param padding:
        """
        self.iconPadding = padding

    def overflowMenuActive(self, active):
        self.overflowMenu = active
        self.flowLayout.allowOverflow(active)

    def setupOverflowMenu(self, btn=None):
        col = (128, 128, 128)
        icon = "sortDown"

        iconIdle = iconlib.iconColorized(icon, size=self.iconSize, color=col)
        iconHover = iconlib.iconColorized(icon, size=self.iconSize, color=colour.offsetColor(col, 40))

        if btn is None:
            btn = iconmenu.IconMenuButton(icon=iconIdle, iconHover=iconHover, parent=self)
            btn.leftClicked.connect(self.showOverflowMenu)
        else:
            btn.setIconIdle(iconIdle)
            btn.setIconHover(iconHover)

        btn.setDoubleClickEnabled(False)
        btn.setProperty("name", "overflow")
        btn.setIconSize(self.getIconSize())
        return btn

    def showOverflowMenu(self):
        self.overflowMenuDlg.show()
        pos = self.overflowMenuBtn.menuPos(QtCore.Qt.AlignRight, self.overflowMenuBtn)
        self.overflowMenuDlg.move(pos)



    def addTool(self, iconName, name, iconColor=(255, 255, 255), doubleClickEnabled=False):
        """Creates a new tool button based on the icon name, and the name.

        :param iconName: Name of the icon to retrieve
        :param name: Name of the tool
        :param iconColor: Color of the icon for the tool
        :param doubleClickEnabled: Enable doubleclick for button
        :return:
        """
        # Create an item with a caption


        btn = iconmenu.IconMenuButton(icon=iconlib.iconColorized(iconName,
                                                                 size=self.iconSize,
                                                                 color=iconColor),
                                      iconHover=iconlib.iconColorized(iconName,
                                                                      size=self.iconSize,
                                                                      color=colour.offsetColor(iconColor, 40)),
                                      parent=self)

        btn.setDoubleClickEnabled(doubleClickEnabled)
        btn.setDoubleClickInterval(150)
        btn.setProperty("name", name)
        btn.setIconSize(self.getIconSize())
        btn.leftClicked.connect(self.toolsClicked)

        self.flowLayout.addWidget(btn)
        self.flowLayout.addWidget(self.overflowMenuBtn)
        return btn

    def getIconSize(self):
        """Returns the icon generated QSize

        :rtype: ::class:`QtCore.QSize`
        """
        return QtCore.QSize(self.iconSize + self.iconPadding,
                            self.iconSize + self.iconPadding)

    def addToolMenu(self, iconName, name, actions, iconColor=(255, 255, 255), showIndicator=True):
        """Adds a new tool menu.

        :param iconName: Name of the icon to retrieve
        :param name: Name of the tool
        :param actions: Actions is a list of tuples with the name and function to run eg ('Name', self.menuItemPressed)
        :param iconColor: The icon color
        :param showIndicator: Show the menu indicator (the arrow in the corner)
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

        self.flowLayout.addWidget(btn)
        self.flowLayout.addWidget(self.overflowMenuBtn)
        return btn

    def clear(self):
        """Clear all widgets
        """
        self.flowLayout.removeWidget(self.overflowMenuBtn)

        self.flowLayout.clear()


    def toolsClicked(self):
        """All buttons will run through here. It will then run a separate function telling which
        button was pressed, along with some other details
        """
        data = self.sender().property("name")
        self.buttonClicked(self.sender(), data)

    def resizeEvent(self, event):
        self.updateWidgets(self.width())
        return
        baseY = self.flowLayout.itemList[0].widget().y()

        for w in self.flowLayout.itemList:
            widget = w.widget()

            if not widget.isVisible():
                widget.show()

            #print(widget.y())

            if widget.y() != baseY:
                widget.hide()

    def updateWidgets(self, width):

        # Stop the flickering
        self.setUpdatesEnabled(False)

        spacing = self.flowLayout.spacingX
        nextX = sum([item.sizeHint().width() + spacing for item in self.flowLayout.items()])

        # Move buttons to dialog layout
        for item in reversed(self.flowLayout.itemList[:-1]):  # overflow button is last we dont want to remove that one
            if nextX > width:
                nextX -= item.sizeHint().width() + spacing
                self.overflowLayout.addWidget(item.widget())

        # Add them back from the flowtoolbar dialogue if need be
        for i in reversed(range(0, self.overflowLayout.count())):
            item = self.overflowLayout.itemAt(i)

            if item is not None:
                itemWidth = item.widget().sizeHint().width()+spacing
                if nextX + itemWidth <= width:
                    self.flowLayout.addWidget(item.widget())
                    self.flowLayout.addWidget(self.overflowMenuBtn)  # Place overflow menu back to the end

                    nextX += itemWidth

        # If the dialog has 1 or more widgets show the overflow menu
        if self.overflowLayout.count() > 0:
            self.overflowMenuBtn.show()
        else:
            self.overflowMenuBtn.hide()

        # If theres only one then add it back and hide the overflow button
        if self.overflowMenuBtn.isVisible() and self.overflowLayout.count() == 1:
            self.flowLayout.addWidget(self.overflowLayout.itemAt(0).widget())
            self.flowLayout.addWidget(self.overflowMenuBtn)
            self.overflowMenuBtn.hide()

        # Re-enable updates
        self.setUpdatesEnabled(True)

    def buttonClicked(self, wgt, name):
        """Overridden by the subclass

        :param wgt: The widget that was pressed, typically a button
        :param name: The name of the tool
        """
        pass

    def setHeight(self, height):
        self.setFixedHeight(height)


class FlowToolbarMenu(dialog.Dialog):
    def __init__(self, parent=None):
        super(FlowToolbarMenu, self).__init__(parent=parent)
        self.mainLayout = utils.vBoxLayout(self)
        self.initUi()

    def initUi(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)

    def layout(self):
        return self.mainLayout

    def sizeHint(self):
        return self.minimumSize()
    
    def show(self, *args, **kwargs):
        super(FlowToolbarMenu, self).show(*args, **kwargs)
        self.resize(self.sizeHint())