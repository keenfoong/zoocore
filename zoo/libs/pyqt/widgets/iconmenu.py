from qt import QtWidgets,QtCore

from zoo.libs.pyqt.widgets.extendedbutton import ExtendedButton
from zoo.libs.pyqt import utils
from zoo.libs import iconlib


class IconMenuButton(ExtendedButton):
    """
    IconMenuButton is a button that only takes an icon. Clicking it will pop up a context menu.
    Left click, middle click and right click can be customized and added with addAction

    .. code-block:: python

        from zoo.libs import iconlib
        logoButton = IconMenuButton(iconlib.icon("magic", size=32))
        logoButton.setIconSize(QtCore.QSize(24, 24))

        # Add to menu. The menu is automatically created if there is none and placed into
        # self.leftMenu, self.middleMenu or self.rightMenu
        logoButton.addAction("Create 3D Characters")
        logoButton.addSeparator()
        logoButton.addAction("Toggle Toolbars", connect=self.toggleContents)

        # Middle Click and right click menu
        logoButton.addAction("Middle Click Menu", mouseMenu=QtCore.Qt.MidButton)
        logoButton.addAction("Right Click Menu", mouseMenu=QtCore.Qt.RightButton)

    """
    def __init__(self, icon=None, iconHover=None, parent=None, doubleClickEnabled=False):
        super(IconMenuButton, self).__init__(icon=icon, iconHover=iconHover, parent=parent,
                                             doubleClickEnabled=doubleClickEnabled)
        self.initUi()

    def initUi(self):
        for m in self.clickMenu.values():
            if m is not None:
                m.setToolTipsVisible(True)

        self.setMenuAlign(QtCore.Qt.AlignRight)


def iconMenuButtonCombo(modes, defaultMode, color=(255, 255, 255), parent=None, size=24, toolTip=""):
    """ Creates an IconMenuButton in a combo box style, like a combo box with an icon instead,
    works with left click and a regular menu

    :example:

        modes = [("arnoldIcon", "Arnold"),
             ("redshiftIcon", "Redshift"),
             ("rendermanIcon", "Renderman")]
        defaultMode = "redshiftIcon"

    :param modes: A list of tuples, tuples are (iconName, menuName)
    :type modes: list(tuples)
    :param defaultMode: the name of the icon to set as the default state
    :type defaultMode: str
    :param color: the color of the icon in 255 rgb color
    :type color: tuple
    :param parent: the parent widget
    :type parent: QWidget
    :param size: the size of the icon
    :type size: int
    :param toolTip: the toolTip on mouse hover
    :type toolTip: str
    :return iconCBtn: the iconCBtn widget
    :rtype iconCBtn: iconmenu.IconMenuButton()
    """
    iconCBtn = IconMenuButton(parent=parent)
    for m in modes:
        iconCBtn.addAction(m[1],
                           mouseMenu=QtCore.Qt.LeftButton,
                           connect=lambda x=m[0]: iconCBtn.setIconByName([x, None], colors=color),
                           icon=iconlib.iconColorized(m[0]))
    iconCBtn.setMenuAlign(QtCore.Qt.AlignRight)
    iconCBtn.setIconByName([defaultMode, None], colors=color)
    iconCBtn.setFixedSize(QtCore.QSize(size, size))
    iconCBtn.setToolTip(toolTip)
    utils.setStylesheetObjectName(iconCBtn, "DefaultButton")
    return iconCBtn

