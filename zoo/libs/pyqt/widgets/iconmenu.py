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
    def __init__(self, icon=None, iconHover=None, parent=None, doubleClickEnabled=False):
        super(IconMenuButton, self).__init__(icon=icon, iconHover=iconHover, parent=parent,
                                             doubleClickEnabled=doubleClickEnabled)
        self.initUi()

    def initUi(self):
        for m in self.clickMenu.values():
            if m is not None:
                m.setToolTipsVisible(True)
