from collections import OrderedDict

from qt import QtWidgets, QtCore, QtGui
from zoo.libs import iconlib
from zoo.libs.pyqt.extended import combobox
from zoo.libs.pyqt import uiconstants
from zoo.libs.pyqt.widgets import frame


class StringEdit(QtWidgets.QWidget):
    textChanged = QtCore.Signal(str)
    buttonClicked = QtCore.Signal()

    def __init__(self, label, placeholder, buttonText=None, parent=None):
        """Creates a label, textbox (QLineEdit) and an optional button
        if the button is None then no button will be created

        :param label: the label name
        :type label: str
        :param placeholder: default text (greyed) inside the textbox (QLineEdit)
        :type placeholder: str
        :param buttonText: optional button name, if None no button will be created
        :type buttonText: str
        :param parent: the qt parent
        :type parent: class
        """
        super(StringEdit, self).__init__(parent=parent)
        self.edit = QtWidgets.QLineEdit(parent=self)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        self.layout.addWidget(QtWidgets.QLabel(label, parent=self))
        self.edit.setPlaceholderText(placeholder)

        self.layout.addWidget(self.edit)
        self.buttonText = buttonText
        if self.buttonText:
            self.btn = QtWidgets.QPushButton(buttonText, self)
            self.layout.addWidget(self.btn)
        self.setLayout(self.layout)
        self.connections()

    def connections(self):
        self.edit.textChanged.connect(self._onTextChanged)
        if self.buttonText:
            self.btn.clicked.connect(self.buttonClicked.emit)

    def _onTextChanged(self):
        self.textChanged.emit(str(self.edit.text()))

    def setText(self, value):
        self.edit.setText(value)

    def text(self):
        return self.edit.text()


class ComboBox(QtWidgets.QWidget):
    itemChanged = QtCore.Signal(int, str)

    def __init__(self, label="", items=(), parent=None):
        """Creates a combo box (drop down menu) with a label

        :param label: the label of the combobox
        :type label: str
        :param items: the item list of the combobox
        :type items: tuple
        :param parent: the qt parent
        :type parent: class
        """
        super(ComboBox, self).__init__(parent=parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        self.box = combobox.ExtendedComboBox(items, parent)

        if label != "":
            self.label = QtWidgets.QLabel(label, parent=self)
            layout.addWidget(self.label)

        layout.addWidget(self.box)
        self.setLayout(layout)

        self.box.currentIndexChanged.connect(self.onItemChanged)

    def __getattr__(self, item):
        if hasattr(self.box, item):
            return getattr(self.box, item)
        super(ComboBox, self).__getAttribute__(item)

    def onItemChanged(self):
        """when the items changed return the tuple of values

        :return valueTuple: the combobox value as an int and the literal string (text)
        :rtype valueTuple: tuple
        """
        self.itemChanged.emit(int(self.box.currentIndex()), str(self.box.currentText()))

    def value(self):
        """returns the literal value of the combo box

        :return value: the literal value of the combo box
        :rtype value: str
        """
        return str(self.box.currentText())

    def currentIndex(self):
        """returns the int value of the combo box

        :return currentIndex: the int value of the combo box
        :rtype currentIndex: int
        """
        return int(self.box.currentIndex())

    def setToText(self, text):
        """Sets the index based on the text

        :param text: Text to search and switch item to.
        :return:
        """
        index = self.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)


class Vector(QtWidgets.QWidget):
    """Vector base Widget for transformations for n axis
    """

    valueChanged = QtCore.Signal(tuple)

    def __init__(self, label, value, min, max, axis, parent=None):
        """Creates a double spinbox for axis and lays them out in a horizontal layout
        We give access to each spinbox with a property eg. self.x which returns the float value

        :param label: the label for the vector eg. translate, if the label is None or "" then it will be excluded
        :type label: str
        :param value: n floats corresponding with axis param
        :type value: tuple(float)
        :param min: the min value for all three elements of the vector
        :type min: float
        :param max: the max value for all three elements of the vector
        :type max: float
        :param axis: every axis which will have a doubleSpinBox eg. [X,Y,Z] or [X,Y,Z,W]
        :param parent: the widget parent
        :type parent: QtWidget
        """
        super(Vector, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.mainLayout.setSpacing(2)
        if label:
            self.label = QtWidgets.QLabel(label, parent=self)
            self.mainLayout.addWidget(self.label)
        self._widgets = OrderedDict()
        for i, v in enumerate(axis):
            box = QtWidgets.QDoubleSpinBox(self)
            box.setObjectName("".join([label, v]))
            box.setRange(min, max)
            box.setValue(value[i])
            box.valueChanged.connect(self.onValueChanged)
            self._widgets[v] = box
            self.mainLayout.addWidget(box)

        self.setLayout(self.mainLayout)

    def __getattr__(self, item):
        widget = self._widgets.get(item)
        if widget is not None:
            return float(widget.value())
        return super(Vector, self).__getAttribute__(item)

    def onValueChanged(self):
        self.valueChanged.emit(tuple([float(i.value()) for i in self._widgets.values()]))

    def widget(self, axis):
        return self._widgets.get(axis)

    def value(self):
        return tuple([float(i.value()) for i in self._widgets.values()])

    def setValue(self, value):
        # get the widgets in order
        keys = self._widgets.keys()
        for i, v in enumerate(value):
            self._widgets[keys[i]].setValue(v)


class Matrix(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(tuple)

    def __init__(self, label, matrix, min, max, parent=None):
        """

        :param label: the matrix widget label
        :type label: str
        :param matrix: a list of lists the lenght of each nested list is equal to the column length of the matrix for
         example if we're dealing with a 4x4 matrix then its a length of 4, 3x3 is 3 etc
        :type matrix: list(list(float))
        :param: min: a list of floats, each float is min for each vector
        :type min: list(float)
        :param: max: a list of floats, each float is max for each vector
        :type max: list(float)
        :param parent:
        :type parent:
        """
        super(Matrix, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.mainLayout.setSpacing(2)
        self.label = QtWidgets.QLabel(label, parent=self)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addWidget(self.label, 0, 0)
        self.mainLayout.addItem(spacerItem, 1, 0)
        self._widgets = OrderedDict()
        axislabels = ("X", "Y", "Z")
        for i, c in enumerate(matrix):
            vec = Vector(label="", value=c, min=min[i], max=max[i], axis=axislabels, parent=self)
            self.mainLayout.addWidget(vec, i, 1)
            self._widgets[i] = vec

        self.setLayout(self.mainLayout)

    def onValueChanged(self):
        """
        :rtype: tuple(tuple(float))
        """
        self.valueChanged.emit(tuple(self._widgets.values()))

    def widget(self, column):
        return self._widgets.get(column)


class Transformation(QtWidgets.QWidget):
    # @todo setup signals
    rotOrders = ("XYZ", "YZX", "ZXY", "XZY", "XYZ", "ZYX")
    axis = ("X", "Y", "Z")
    valueChanged = QtCore.Signal(list, list, list, str)

    def __init__(self, parent=None):
        super(Transformation, self).__init__(parent=parent)
        # self.group = QtWidgets.QGroupBox(parent=self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
        # self.group.setLayout(self.layout)
        self.translationVec = Vector("Translation:", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        self.rotationVec = Vector("Rotation:", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        self.scaleVec = Vector("Scale:", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        self.rotationOrderBox = ComboBox("RotationOrder:", Transformation.rotOrders, parent=self)
        self.layout.addWidget(self.translationVec)
        self.layout.addWidget(self.rotationVec)
        self.layout.addWidget(self.rotationVec)
        self.layout.addWidget(self.scaleVec)
        self.layout.addWidget(self.rotationOrderBox)

        self.setLayout(self.layout)

    def onValueChanged(self, value):
        self.valueChanged.emit(self.translationVec.value(),
                               self.rotationVec.value(),
                               self.scaleVec.value(),
                               self.rotationOrderBox.value())

    def translation(self):
        return self.translationVec.value()

    def rotation(self):
        return self.rotationVec.value()

    def scale(self):
        return self.scaleVec.value()

    def rotationOrder(self):
        """:return: int of the rotation order combo box, not the str
        :rtype: int
        """
        return int(self.rotationOrderBox.currentIndex())

    def rotationOrderValue(self):
        """:return: str of the rotation order combo box, the literal value
        :rtype: str
        """
        return self.rotationOrderBox.value()


class OkCancelButtons(QtWidgets.QWidget):
    OkBtnPressed = QtCore.Signal()
    CancelBtnPressed = QtCore.Signal()

    def __init__(self, okText="OK", cancelTxt="Cancel", parent=None):
        """Creates OK Cancel Buttons bottom of window, can change the names

        :param okText: the text on the ok (first) button
        :type okText: str
        :param cancelTxt: the text on the cancel (second) button
        :type cancelTxt: str
        :param parent: the widget parent
        :type parent: class
        """
        super(OkCancelButtons, self).__init__(parent=parent)
        self.layout = QtWidgets.QHBoxLayout()
        self.okBtn = QtWidgets.QPushButton(okText, parent=self)
        self.cancelBtn = QtWidgets.QPushButton(cancelTxt, parent=self)
        self.layout.addWidget(self.okBtn)
        self.layout.addWidget(self.cancelBtn)
        self.setLayout(self.layout)
        self.connections()

    def connections(self):
        self.okBtn.clicked.connect(self.OkBtnPressed.emit)
        self.cancelBtn.clicked.connect(self.CancelBtnPressed.emit)


class HRadioButtonGroup(QtWidgets.QWidget):
    toggled = QtCore.Signal(int)

    def __init__(self, radioList=None, default=0, parent=None):
        super(HRadioButtonGroup, self).__init__(parent=parent)
        if radioList is None:
            radioList = []

        self.radioButtons = []
        self.group = QtWidgets.QButtonGroup(parent=self)
        hRadioLayout = QtWidgets.QHBoxLayout()
        for radioName in radioList:
            newRadio = QtWidgets.QRadioButton(radioName, self)
            self.group.addButton(newRadio)
            hRadioLayout.addWidget(newRadio)
            self.radioButtons.append(newRadio)

        if default is not None and default < len(self.radioButtons):
            self.radioButtons[default].setChecked(True)
        self.group.buttonClicked.connect(self.toggled.emit)
        self.setLayout(hRadioLayout)

    def getChecked(self):
        """
        Returns the widget that is checked
        :return:
        :type: QtWidgets.QRadioButton()
        """
        for r in self.radioButtons:
            if r.isChecked():
                return r


class labelColorBtn(QtWidgets.QWidget):
    def __init__(self, label="Color:", initialRgbColor=(255, 0, 0), initialRgbColorF=None, parent=None):
        """Creates a label and a color button (with no text) which opens a QT color picker,
        returns both rgb (0-255) and rgbF (0-1.0) values

        :param label: The name of the label, usually "Color:"
        :type label: str
        :param initialRgbColor: The initial rgb color in 0-255 ranges, overridden if there's a initialRgbColorF value
        :type initialRgbColor: tuple
        :param initialRgbColorF: The initial rgb color in 0-1.0 ranges, if None defaults to initialRgbColor values
        :type initialRgbColorF: tuple
        :param parent: the widget parent
        :type parent: class
        """
        super(labelColorBtn, self).__init__(parent=parent)
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(QtWidgets.QLabel(label, parent=self))
        self.colorPickerBtn = QtWidgets.QPushButton("", parent=self)
        if not initialRgbColorF:  # if initialRgbColorF is None then input values are in 0-255 range
            self.storedRgbColor = initialRgbColor
        else:  # if initialRgbColorF exists then input values are in 0.0-1.0 range
            self.storedRgbColor = tuple([i * 255 for i in initialRgbColorF])
        self.colorPickerBtn.setStyleSheet("background-color: rgb{}".format(str(self.storedRgbColor)))
        self.layout.addWidget(self.colorPickerBtn)
        self.setLayout(self.layout)
        self.connections()

    def pickColor(self):
        """Opens the color picker window
        If ok is pressed then the new color is returned in 0-255 ranges Eg (128, 255, 12)
        If Cancel is pressed the color is invalid and nothing happens
        """
        initialPickColor = QtGui.QColor(self.storedRgbColor[0], self.storedRgbColor[1], self.storedRgbColor[2], 255)
        color = QtWidgets.QColorDialog.getColor(initialPickColor)
        if QtGui.QColor.isValid(color):  # if the user hits cancel the returned color is invalid, so don't update
            self.storedRgbColor = (color.getRgb())[0:3]
            self.colorPickerBtn.setStyleSheet("background-color: {}".format(color.name()))

    def rgbColor(self):
        """returns rgb tuple with 0-255 ranges Eg (128, 255, 12)
        """
        return self.storedRgbColor

    def rgbColorF(self):
        """returns rgb tuple with 0-1.0 float ranges Eg (1.0, .5, .6666)
        """
        return tuple(float(i) / 255 for i in self.storedRgbColor)

    def connections(self):
        """Open the color picker when the button is pressed
        """
        self.colorPickerBtn.clicked.connect(self.pickColor)


class CollapsableFrameLayout(QtWidgets.QWidget):
    closeRequested = QtCore.Signal()
    openRequested = QtCore.Signal()
    _collapsedIcon = iconlib.icon("sortClosed")
    _expandIcon = iconlib.icon("sortDown")

    def __init__(self, title, collapsed=False, collapsable=True, contentMargins=uiconstants.MARGINS,
                 contentSpacing=uiconstants.SPACING, color=uiconstants.DARKBGCOLOR,
                 parent=None):
        """Collapsable framelayout, similar to Maya's cmds.frameLayout
        Title is inside a bg colored frame layout that can open and collapse
        Code example for how to use is as follows...

            self.collapseLayout = layouts.collapsableFrameLayout("Custom Title Goes Here", parent=self)
            self.collapseLayout.addWidget(self.customWidget)  # for adding widgets
            self.collapseLayout.addLayout(self.customLayout)  # for adding layouts

        :param title: The name of the collapsable frame layout
        :type title: str
        :param collapsed: Is the default state collapsed, if False it's open
        :type collapsed: bool
        :param collapsable: Are the contents collapsable? If False the contents are always open
        :type collapsed: bool
        :param contentMargins: The margins for the collapsable contents section, left, top, right, bottom (pixels)
        :type contentMargins: tuple
        :param contentSpacing: spacing (padding) for the collapsable contents section, in pixels
        :type contentSpacing: int
        :param parent: the widget parent
        :type parent: class
        """
        super(CollapsableFrameLayout, self).__init__(parent=parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.title = title
        self.color = color
        self.contentMargins = contentMargins
        self.contentSpacing = contentSpacing
        self.collapsable = collapsable
        self.collapsed = collapsed
        if not collapsable:  # if not collapsable must be open
            self.collapsed = False
        self.initUi()
        self.setLayout(self.layout)
        self.connections()

    def initUi(self):
        """Builds the UI, the title and the collapsable widget that' the container for self.hiderLayout
        """
        self.buildTitleFrame()
        self.buildHiderWidget()
        self.layout.addWidget(self.titleFrame)
        self.layout.addWidget(self.widgetHider)

    def buildTitleFrame(self):
        """Builds the title part of the layout with a QFrame widget
        """
        # main dark grey qframe
        self.titleFrame = frame.QFrame(parent=self)
        self.setFrameColor(self.color)
        self.titleFrame.setContentsMargins(4, 0, 4, 0)
        # the horizontal layout
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.titleFrame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        # the icon and title and spacer
        self.iconButton = QtWidgets.QToolButton(parent=self)
        if self.collapsed:
            self.iconButton.setIcon(self._collapsedIcon)
        else:
            self.iconButton.setIcon(self._expandIcon)
        self.titleLabel = QtWidgets.QLabel(self.title, parent=self)
        self.titleLabel.setStyleSheet("font: bold;")
        self.titleLabel.setContentsMargins(0, 0, 0, 0)
        spacerItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # add to horizontal layout
        self.horizontalLayout.addWidget(self.iconButton)
        self.horizontalLayout.addWidget(self.titleLabel)
        self.horizontalLayout.addItem(spacerItem)
        self.titleFrame.setFixedHeight(self.titleFrame.sizeHint().height())
        self.setMinimumSize(self.titleFrame.sizeHint().width(), self.titleFrame.sizeHint().height())

    def setFrameColor(self, color):
        self.titleFrame.setStyleSheet("background-color: rgb{0}; "
                                      "border-radius: 3px;"
                                      "border: 1px solid rgb{0}".format(str(color)))

    def addWidget(self, widget):
        self.hiderLayout.addWidget(widget)

    def addLayout(self, layout):
        self.hiderLayout.addLayout(layout)

    def buildHiderWidget(self):
        """Builds widget that is collapsable
        Widget can be toggled so it's a container for the layout
        """
        self.widgetHider = QtWidgets.QFrame()
        self.widgetHider.setContentsMargins(0, 0, 0, 0)
        self.hiderLayout = QtWidgets.QVBoxLayout(self.widgetHider)
        self.hiderLayout.setContentsMargins(*self.contentMargins)
        self.hiderLayout.setSpacing(self.contentSpacing)
        self.widgetHider.setHidden(self.collapsed)

    def onCollapsed(self):
        self.widgetHider.setHidden(True)
        self.iconButton.setIcon(self._collapsedIcon)
        self.closeRequested.emit()
        self.collapsed = 1

    def onExpand(self):
        self.widgetHider.setHidden(False)
        self.iconButton.setIcon(self._expandIcon)
        self.openRequested.emit()
        self.collapsed = 0

    def showHideWidget(self, *args):
        """Shows and hides the widget `self.widgetHider` this contains the layout `self.hiderLayout`
        which will hold the custom contents that the user specifies
        """
        if not self.collapsable:
            return
        # If we're already collapsed then expand the layout
        if self.collapsed:
            self.onExpand()
            return
        self.onCollapsed()

    def connections(self):
        """toggle widgetHider vis
        """
        self.iconButton.clicked.connect(self.showHideWidget)
        self.titleFrame.mouseReleased.connect(self.showHideWidget)


class HotkeyDetectEdit(QtWidgets.QLineEdit):
    hotkeyEdited = QtCore.Signal()

    def __init__(self, text="", parent=None, prefix="", suffix=""):
        """ A line Edit which detects key combinations are being pressed(for hotkeys for instance).

        Usage: It works similarly to a QLineEdit. Type in a hotkey combination to show the hotkey.

        Example::

            # eg Type in Ctrl+Alt+P and it would set the text of the QLineEdit to "Ctrl+Alt+P"
            wgt = HotkeyDetectEdit()

        :param text:
        :param parent:
        :param prefix:
        :param suffix:
        """
        super(HotkeyDetectEdit, self).__init__(parent)

        self.prefix = prefix
        self.suffix = suffix

        self.setText(text)
        self.backspaceClears = True

        # str.maketrans('~!@#$%^&*()_+{}|:"<>?', '`1234567890-=[]\\;\',./')
        self.specialkeys = {64: 50, 33: 49, 34: 39, 35: 51, 36: 52, 37: 53, 38: 55, 40: 57, 41: 48, 42: 56, 43: 61,
                            63: 47, 60: 44, 126: 96, 62: 46, 58: 59, 123: 91, 124: 92, 125: 93, 94: 54, 95: 45}

    def setText(self, text, resetCursor=True):
        """ Set text of HotKeyEdit

        :param text:
        :param resetCursor:
        :return:
        """
        text = self.prefix + text + self.suffix

        super(HotkeyDetectEdit, self).setText(text)

        if resetCursor:
            self.setCursorPosition(0)

    def keyPressEvent(self, e):
        """ Update the text edit to whatever the hotkey is inputted

        For example type in Ctrl+Alt+P and it would set the text of the QLineEdit to "Ctrl+Alt+P"

        :param e:
        :return:
        """
        keyStr = QtGui.QKeySequence(self.convertSpecChars(e.key())).toString()

        # Return out if its only a modifier
        if str(e.text()) == "":
            return

        self.text()
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        # Feels like theres a better way to do this..
        if modifiers == QtCore.Qt.ShiftModifier:
            hotkey = 'Shift+' + keyStr
        elif modifiers == QtCore.Qt.ControlModifier:
            hotkey = 'Ctrl+' + keyStr
        elif modifiers == QtCore.Qt.AltModifier:
            hotkey = 'Alt+' + keyStr
        elif modifiers == (QtCore.Qt.AltModifier | QtCore.Qt.ControlModifier):
            hotkey = 'Ctrl+Alt+' + keyStr
        elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            hotkey = 'Ctrl+Shift+' + keyStr
        elif modifiers == (QtCore.Qt.AltModifier | QtCore.Qt.ShiftModifier):
            hotkey = 'Shift+Alt+' + keyStr
        elif modifiers == (QtCore.Qt.AltModifier | QtCore.Qt.ControlModifier |
                               QtCore.Qt.ShiftModifier):
            hotkey = 'Ctrl+Alt+Shift+' + keyStr
        elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            hotkey = 'Ctrl+' + keyStr
        else:
            hotkey = keyStr

        if (hotkey == "Backspace" and self.backspaceClears) or hotkey == "Esc":
            hotkey = ""

        self.setText(hotkey)
        self.hotkeyEdited.emit()

    def convertSpecChars(self, charInt):
        """ Converts special characters back to the original keyboard number

        :param charInt:
        :return:
        """
        if charInt in self.specialkeys:
            return self.specialkeys[charInt]
        return charInt


class ClippedLabel(QtWidgets.QLabel):
    _width = _text = _elided = None
    def __init__(self, text='', width=0, parent=None, ellipsis=True):
        """ Label that will clip itself if the widget width is smaller than the text

        QLabel doesn't do this, so we have to do this here.

        Appropriated from:
        https://stackoverflow.com/questions/35080148/how-to-hide-or-cut-a-qwidget-text-when-i-change-main-window-size

        :param text:
        :param width:
        :param parent:
        """
        super(ClippedLabel, self).__init__(text, parent)
        self.setMinimumWidth(width if width > 0 else 1)
        self.ellipsis = ellipsis

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.drawFrame(painter)
        margin = self.margin()
        rect = self.contentsRect()
        rect.adjust(margin, margin, -margin, -margin)
        text = self.text()
        width = rect.width()
        if text != self._text or width != self._width:
            self._text = text
            self._width = width
            self._elided = self.fontMetrics().elidedText(
                text, QtCore.Qt.ElideRight, width)
        option = QtWidgets.QStyleOption()
        option.initFrom(self)

        if self.ellipsis:
            self.style().drawItemText(
                painter, rect, self.alignment(), option.palette,
                self.isEnabled(), self._elided, self.foregroundRole())
        else:
            self.style().drawItemText(
                painter, rect, self.alignment(), option.palette,
                self.isEnabled(), self.text(), self.foregroundRole())


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        """ A nice horizontal line to space ui """
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class QVLine(QtWidgets.QFrame):
    def __init__(self):
        """ A nice vertical line to space ui """
        super(QVLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)