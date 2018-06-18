from qt import QtWidgets, QtCore

from zoo.libs import iconlib
from zoo.libs.utils import colour


class ExtendedButton(QtWidgets.QPushButton):
    """
    Push Button that allows you to have the left click, middle click, and right click.

    Each click allows for a menu
    """

    leftClicked = QtCore.Signal()
    middleClicked = QtCore.Signal()
    rightClicked = QtCore.Signal()

    leftMenu = None
    middleMenuActive = None
    rightMenuActive = None

    def __init__(self, icon=None, iconName=None, iconSize=32, iconColor=(255,255,255), iconOverlayName=None,
                 iconHoverOffset=40,
                 text=None, parent=None,
                 leftClickMenu=None, middleClickMenu=None, rightClickMenu=None):

        self.buttonIcon = icon or iconlib.iconColorized(iconName, size=iconSize, color=iconColor, overlayName=iconOverlayName)
        self.buttonIconHover = icon or iconlib.iconColorized(iconName,
                                                     size=iconSize, color=self.offsetColor(iconColor, iconHoverOffset),
                                                     overlayName=iconOverlayName)

        super(ExtendedButton, self).__init__(icon=self.buttonIcon, text=text, parent=parent)

        self.leftMenu = leftClickMenu
        self.middleMenu = middleClickMenu
        self.rightMenu = rightClickMenu

        self.leftMenuActive = True
        self.middleMenuActive = True
        self.rightMenuActive = True

        self.leftClicked.connect(self.leftContextMenu)
        self.middleClicked.connect(self.middleContextMenu)
        self.rightClicked.connect(self.rightContextMenu)

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.MiddleButton:
                self.setDown(True)
            elif event.button() == QtCore.Qt.RightButton:
                self.setDown(True)

        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.setDown(False)
            if event.button() == QtCore.Qt.LeftButton:
                self.leftClicked.emit()
            elif event.button() == QtCore.Qt.MiddleButton:
                self.middleClicked.emit()
            elif event.button() == QtCore.Qt.RightButton:
                self.rightClicked.emit()

        # Mouse icon hover
        if event.type() == QtCore.QEvent.Enter:
            self.setIcon(self.buttonIconHover)

        elif event.type() == QtCore.QEvent.Leave:
            self.setIcon(self.buttonIcon)

        return super(ExtendedButton, self).eventFilter(object, event)

    def offsetColor(self, col, offset=0, saturation=0.5):
        """
        Returns a darker colour
        :param col:
        :param offset:
        :return:
        """
        col = (colour.clamp(col[0] + offset), colour.clamp(col[1] + offset), colour.clamp(col[2] + offset))
        #col = tuple(colour.convertHsvToRgb(colour.offsetSaturation(colour.convertRgbToHsv(list(col)), saturation)))

        return col


    def leftContextMenu(self):
        """
        Display the left context menu
        :return:
        """
        if self.leftMenu is not None and self.leftMenuActive:
            self.leftMenu.exec_(self.menuPos())

    def middleContextMenu(self):
        """
        Display the middle context menu
        :return:
        """
        if self.middleMenu is not None and self.middleMenuActive:
            self.middleMenu.exec_(self.menuPos())

    def rightContextMenu(self):
        """
        Display the right context menu
        :return:
        """
        if self.rightMenu is not None and self.rightMenuActive:
            self.rightMenu.exec_(self.menuPos())

    def menuPos(self):
        """
        Get menu position based on the current widget position and perimeter
        :return:
        """
        point = self.rect().bottomLeft()
        return self.mapToGlobal(point)