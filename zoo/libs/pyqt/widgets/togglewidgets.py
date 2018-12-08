from qt import QtWidgets, QtGui, QtCore

from zoo.libs import iconlib
from zoo.libs.pyqt import utils
from zoo.libs.pyqt.widgets import extendedbutton
from zoo.libs.utils import colour


class CheckableIcons(extendedbutton.ButtonIcons):
    """ImageRadioButton and ImageCheckBox inherits from this this class to set up the icons that
    change on mouse over, press and release. Also the icons change when the button is checked or unchecked.

    .. code-block:: python

        class ImageRadioButton(QtWidgets.QRadioButton, Checkable):
            def __init__():
                self.initCheckables(uncheckedIconName="circle",
                        checkedIconName="circleFilled",
                        pressedIconName="circleFilled")

    Must use initCheckables() when inherited in a subclass

    """
    def __init__(self):
        super(CheckableIcons, self).__init__()

    def toggleClicked(self):

        if self.isChecked():
            self.setIconByName(iconName=self.iconChecked, colorOffset=40)
        else:
            self.setIconByName(iconName=self.iconUnchecked, colorOffset=40)

    def initCheckables(self, uncheckedIconName, checkedIconName, pressedIconName):

        className = self.__class__.__name__

        style = """
        {0}::indicator {{background-color:transparent; width:0}}
        """.format(className)
        self.setStyleSheet(style)

        self.iconUnchecked = uncheckedIconName
        self.iconChecked = checkedIconName
        self.iconPressed = pressedIconName

        self.toggled.connect(self.toggleClicked)
        self.pressed.connect(self.buttonPressed)
        self.released.connect(self.buttonReleased)

        self.toggleClicked()

    def buttonPressed(self):
        pressedCol = colour.offsetColor(self.iconColor, -30)
        self.originalColor = self.iconColor
        self.setIconByName(iconName=self.iconPressed, color=pressedCol)

    def buttonReleased(self):
        self.setIconColor(self.originalColor, update=True)

    def paintEvent(self, e):
        super(CheckableIcons, self).paintEvent(e)


class ImageRadioButton(QtWidgets.QRadioButton, CheckableIcons):

    def __init__(self, text,
                 checkedIcon="circleFilled",
                 uncheckedIcon="circle",
                 pressedIcon="circleFilled",
                 color=(128, 128, 128),
                 highlight=40, parent=None):
        super(ImageRadioButton, self).__init__(parent=parent, text=text)

        self.highlightOffset = highlight
        self.setIconSize(QtCore.QSize(12, 12))
        self.setIconColor(color)

        # Initialise the icons
        self.initCheckables(uncheckedIconName=uncheckedIcon,
                            checkedIconName=checkedIcon,
                            pressedIconName=pressedIcon)


class ImageCheckBox(QtWidgets.QCheckBox, CheckableIcons):
    def __init__(self, text,
                 checkedIcon="roundedSquareFilledBox",
                 uncheckedIcon="roundedsquare",
                 pressedIcon="roundedSquareFilledBox",
                 color=(128, 128, 128),
                 highlight=40, parent=None):
        super(ImageCheckBox, self).__init__(parent=parent, text=text)

        self.highlightOffset = highlight
        self.setIconSize(QtCore.QSize(12, 12))
        self.setIconColor(color)

        # Initialise the icons
        self.initCheckables(uncheckedIconName=uncheckedIcon,
                            checkedIconName=checkedIcon,
                            pressedIconName=pressedIcon)






