from collections import OrderedDict

from qt import QtWidgets, QtCore, QtGui
from zoo.libs import iconlib
from zoo.libs.pyqt.extended import combobox
from zoo.libs.pyqt import uiconstants, utils
from zoo.libs.pyqt.widgets import frame, extendedbutton

def Label(name, parent, toolTip=""):
    """One liner for labels and tooltip

    :param name: name of the text label
    :type name: str
    :param parent: the qt parent
    :type parent: class
    :param toolTip: the tool tip message on mouse over hover, extra info
    :type toolTip: str
    :return lbl: the QT QLabel widget
    :rtype lbl: QWidget.QLabel
    """
    lbl = QtWidgets.QLabel(name, parent=parent)
    lbl.setToolTip(toolTip)
    return lbl


def LineEdit(text="", placeholder="", parent=None, toolTip="", editWidth=None, inputMode="string"):
    """Creates a simple textbox (QLineEdit)

    :param text:
    :param placeholder the default text in the text box
    :type placeholder: str or float or int
    :param parent: the qt parent
    :type parent: class
    :param toolTip: the tool tip message on mouse over hover, extra info
    :type toolTip: str
    :param editWidth: the width of the textbox in pixels optional, None is ignored
    :type editWidth: int
    :param inputMode: restrict the user to this data entry, "string" text, "float" decimal or "int" no decimal
    :type inputMode: str
    :return textBox: the QT QLabel widget
    :rtype textBox: QWidget.QLabel
    """
    textBox = QtWidgets.QLineEdit(parent=parent)
    # todo: STYLESHEET hardcoded color & margins here as a temp workaround, this should be in stylesheets
    textBox.setStyleSheet("QLineEdit {background: rgb(27, 27, 27);}")
    if inputMode == "float":  # todo: this should be a constant
        placeholder = str(placeholder)
        textBox.setValidator(QtGui.QDoubleValidator())
    elif inputMode == "int":
        placeholder = int(placeholder)
        textBox.setValidator(QtGui.QIntValidator())
    textBox.setTextMargins(*utils.marginsDpiScale(2, 2, 2, 2))
    if editWidth:
        textBox.setFixedWidth(utils.dpiScale(editWidth))
    textBox.setPlaceholderText(placeholder)
    textBox.setText(str(text))
    textBox.setToolTip(toolTip)
    return textBox


class StringEdit(QtWidgets.QWidget):
    textChanged = QtCore.Signal(str)
    buttonClicked = QtCore.Signal()
    editingFinished = QtCore.Signal()

    def __init__(self, label, editText="", editPlaceholder="", buttonText=None, parent=None, editWidth=None,
                 labelRatio=1, btnRatio=1, editRatio=1, toolTip="", inputMode="string"):
        """Creates a label, textbox (QLineEdit) and an optional button
        if the button is None then no button will be created

        :param label: the label name
        :type label: str
        :param placeholderText: default text is greyed out inside the textbox if true (QLineEdit)
        :type placeholderText: bool
        :param buttonText: optional button name, if None no button will be created
        :type buttonText: str
        :param parent: the qt parent
        :type parent: class
        :param editWidth: the width of the textbox in pixels optional, None is ignored
        :type editWidth: int
        :param labelRatio: the width ratio of the label/text/button corresponds to the ratios of ratioEdit/ratioBtn
        :type labelRatio: int
        :param btnRatio: the width ratio of the label/text/button corresponds to the ratios of editRatio/labelRatio
        :type btnRatio: int
        :param editRatio: the width ratio of the label/text/button corresponds to the ratios of labelRatio/btnRatio
        :type editRatio: int
        :param toolTip: the tool tip message on mouse over hover, extra info
        :type toolTip: str
        :param inputMode: restrict the user to this data entry, "string" text, "float" decimal or "int" no decimal
        :type inputMode: str
        :return StringEdit: returns the class with various options, see the methods
        :rtype StringEdit: QWidget
        """
        super(StringEdit, self).__init__(parent=parent)
        self.layout = HBoxLayout(parent, (0, 0, 0, 0), spacing=uiconstants.SREG)
        self.edit = LineEdit(editText, editPlaceholder, parent, toolTip, editWidth, inputMode)
        self.label = Label(label, parent, toolTip)
        self.layout.addWidget(self.label, labelRatio)
        self.layout.addWidget(self.edit, editRatio)
        self.buttonText = buttonText
        if self.buttonText:
            # todo button connections should be added from this class (connections)
            self.btn = extendedbutton.buttonStyle(self.buttonText, toolTip=toolTip, style=uiconstants.BTN_DEFAULT)
            self.layout.addWidget(self.btn, btnRatio)
        self.setLayout(self.layout)
        self.connections()

    def connections(self):
        """connects the buttons and text changed emit"""
        self.edit.textChanged.connect(self._onTextChanged)
        if self.buttonText:
            self.btn.clicked.connect(self.buttonClicked.emit)

        self.editingFinished = self.edit.editingFinished

    def _onTextChanged(self):
        """If the text is changed emit"""
        self.textChanged.emit(str(self.edit.text()))

    def setDisabled(self, state):
        """Disable the text (make it grey)"""
        self.edit.setDisabled(state)

    def setText(self, value):
        """Change the text at any time"""
        self.edit.setText(value)

    def text(self):
        """get the text of self.edit"""
        return self.edit.text()


class ComboBoxSearchable(QtWidgets.QWidget):
    itemChanged = QtCore.Signal(int, str)

    def __init__(self, label="", items=(), parent=None, labelRatio=None, boxRatio=None, toolTip="", setIndex=0):
        """Creates a searchable combo box (drop down menu) with a label

        :param label: the label of the combobox
        :type label: str
        :param items: the item list of the combobox
        :type items: tuple
        :param parent: the qt parent
        :type parent: class
        """
        super(ComboBoxSearchable, self).__init__(parent=parent)
        layout = HBoxLayout(parent=None, margins=(0, 0, 0, 0),
                            spacing=utils.dpiScale(uiconstants.SPACING))  # margins kwarg should be added
        self.box = combobox.ExtendedComboBox(items, parent)
        self.box.setToolTip(toolTip)
        if setIndex:
            self.box.setCurrentIndex(setIndex)
        if label:
            self.label = Label(label, parent, toolTip)
            if labelRatio:
                layout.addWidget(self.label, labelRatio)
            else:
                layout.addWidget(self.label)
        if boxRatio:
            layout.addWidget(self.box, boxRatio)
        else:
            layout.addWidget(self.box)
        layout.addWidget(self.box)
        self.setLayout(layout)

        self.box.currentIndexChanged.connect(self.onItemChanged)

    def __getattr__(self, item):
        if hasattr(self.box, item):
            return getattr(self.box, item)
        super(ComboBoxSearchable, self).__getAttribute__(item)

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


class ComboBoxRegular(QtWidgets.QWidget):
    """Creates a regular "not searchable" combo box (drop down menu) with a label
    """
    itemChanged = QtCore.Signal(int, str)

    def __init__(self, label="", items=(), parent=None, labelRatio=None, boxRatio=None, toolTip="", setIndex=0):
        """initialize class

        :param label: the label of the combobox
        :type label: str
        :param items: the item list of the combobox
        :type items: list
        :param parent: the qt parent
        :type parent: class
        :param toolTip: the tooltip info to display with mouse hover
        :type toolTip: str
        :param setIndex: set the combo box value as an int - 0 is the first value, 1 is the second
        :type setIndex: int
        """
        super(ComboBoxRegular, self).__init__(parent=parent)

        if items is None:
            items = []

        layout = HBoxLayout(parent=None, margins=utils.marginsDpiScale(0, 0, 0, 0),
                            spacing=utils.dpiScale(uiconstants.SREG))  # margins kwarg should be added
        self.box = QtWidgets.QComboBox(parent)
        self.box.addItems(items)
        self.box.setToolTip(toolTip)
        if label != "":
            self.label = Label(label, parent, toolTip)
            if labelRatio:
                layout.addWidget(self.label, labelRatio)
            else:
                layout.addWidget(self.label)
        if boxRatio:
            layout.addWidget(self.box, boxRatio)
        else:
            layout.addWidget(self.box)
        if setIndex:
            self.box.setCurrentIndex(setIndex)
        self.setLayout(layout)

        self.box.currentIndexChanged.connect(self.onItemChanged)

    def __getattr__(self, item):
        if hasattr(self.box, item):
            return getattr(self.box, item)
        super(ComboBoxRegular, self).__getAttribute__(item)

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


def CheckBoxRegular(label="", setChecked=False, parent=None, toolTip=""):
    """Creates a regular check box (on off) with extra simple options

    :param label: the label of the checkbox
    :type label: string
    :param setChecked: the default state of the checkbox (True on, False off)
    :type setChecked: bool
    :param parent: the qt parent
    :type parent: class
    :param toolTip: the tooltip info to display with mouse hover
    :type toolTip: str
    :return qWidget: the checkbox qt widget
    :rtype value: object
    """
    box = QtWidgets.QCheckBox(label, parent=parent)
    box.setToolTip(toolTip)
    if setChecked:
        box.setChecked(setChecked)
    # todo: STYLESHEET hardcoded color here as a temp workaround, should be in stylesheets
    box.setStyleSheet("QCheckBox::indicator:checked, QCheckBox::indicator:unchecked "
                       "{background: rgb(27, 27, 27);}")
    return box


class VectorLineEdit(QtWidgets.QWidget):
    """A label with multiple QLineEdits (text boxes), no spin boxes usually for x y z numeric input
    use inputMode="float" to restrict the data entry to decimal numbers
    """
    textChanged = QtCore.Signal(tuple)

    def __init__(self, label, value, axis=("x", "y", "z"), parent=None, toolTip="", inputMode="float", labelRatio=1,
                 editRatio=1, spacing=uiconstants.SREG):
        """A label with multiple QLineEdits (text boxes), no spin boxes usually for x y z numeric input
        use inputMode="float" to restrict the data entry to decimal numbers

        :param label: the label for the vector eg. translate, if the label is None or "" then it will be excluded
        :type label: str
        :param value: n floats corresponding with axis param
        :type value: tuple(float)
        :param axis: every axis which will have a doubleSpinBox eg. ("x", "y", "z") or ("x", "y", "z", "w")
        :type axis: tuple(str)
        :param parent: the widget parent
        :type parent: QtWidget
        :param inputMode: restrict the user to this data entry, "string" text, "float" decimal or "int" no decimal
        :type inputMode: str
        :param labelRatio: the width ratio of the label/edit boxes, the "label" ratio when compared to the "edit boxes"
        :type labelRatio: int
        :param editRatio: the width ratio of the label/edit boxes, the "edit boxes" ratio when compared to the label
        :type editRatio: int
        :param spacing: the spacing of each widget
        :type spacing: int
        """
        super(VectorLineEdit, self).__init__(parent=parent)
        self.mainLayout = HBoxLayout(parent, (0, 0, 0, 0), spacing)
        if label:
            self.label = QtWidgets.QLabel(label, parent=self)
            self.mainLayout.addWidget(self.label, labelRatio)
        self._widgets = OrderedDict()
        vectorEditLayout = HBoxLayout(parent, (0, 0, 0, 0), spacing)
        for i, v in enumerate(axis):
            edit = LineEdit(value[i], False, parent, toolTip, inputMode=inputMode)
            edit.setObjectName("".join([label, v]))
            edit.textChanged.connect(self._onTextChanged)
            self._widgets[v] = edit
            vectorEditLayout.addWidget(edit)
        self.mainLayout.addLayout(vectorEditLayout, editRatio)
        self.setLayout(self.mainLayout)

    def _onTextChanged(self):
        """updates the text, should also update the dict
        """
        # todo: check that the methods below work, not tested
        self.textChanged.emit(tuple([float(i.value()) for i in self._widgets.text()]))

    def widget(self, axis):
        """Gets the widget from the axis string name

        :param axis: the single axis eg. "x"
        :type axis: tuple(str)
        :return widget: the LineEdit as a widget
        :rtype widget: QWidget
        """
        return self._widgets.get(axis)

    def value(self):
        """Gets the tuple values (text) of all the QLineEdits

        :return textValues: a tuple of string values from each QLineEdit textbox
        :rtype textValues: tuple(str)
        """
        return tuple([float(i.value()) for i in self._widgets.text()])

    def setValue(self, value):
        """Sets the text values of all the QLineEdits, can be strings floats or ints depending on the inputMode

        :param value: the value of all text boxes, as a list of strings (or floats, ints depending on inputMode)
        :type value: tuple
        """
        # get the widgets in order
        keys = self._widgets.keys()
        for i, v in enumerate(value):
            self._widgets[keys[i]].setText(v)


class VectorSpinBox(QtWidgets.QWidget):
    """Vector base Widget with spin box for transformations for n axis
    3 x QDoubleSpinBox (numerical textEdit with spinBox)
    """

    valueChanged = QtCore.Signal(tuple)

    def __init__(self, label, value, min, max, axis, parent=None, step=0.1, setDecimals=2):
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
        :type axis: list
        :param parent: the widget parent
        :type parent: QtWidget
        :param step: the step amount while clicking on the spin box or keyboard up/down
        :type step: float
        """
        super(VectorSpinBox, self).__init__(parent=parent)
        self.mainLayout = HBoxLayout(parent, (2, 2, 2, 2), uiconstants.SREG)
        if label:
            self.label = QtWidgets.QLabel(label, parent=self)
            self.mainLayout.addWidget(self.label)
        self._widgets = OrderedDict()
        # todo: STYLESHEET needs to be in stylesheet and prefs
        # rgb(27, 27, 27) is the QLineEdit/QDoubleSpinBox color
        # images will need to be added and tweaked for hover states and press
        borderSize = utils.dpiScale(3)
        styleSheet = "QDoubleSpinBox {0} border: {2}px solid rgb(27, 27, 27); " \
                     "border-radius: 0px; {1}".format("{", "}", borderSize)

        for i, v in enumerate(axis):
            box = QtWidgets.QDoubleSpinBox(self)
            box.setSingleStep(step)
            box.setObjectName("".join([label, v]))
            box.setRange(min, max)
            box.setValue(value[i])
            box.setDecimals(setDecimals)
            box.valueChanged.connect(self.onValueChanged)
            box.setStyleSheet(styleSheet)
            self._widgets[v] = box
            self.mainLayout.addWidget(box)

        self.setLayout(self.mainLayout)

    def __getattr__(self, item):
        widget = self._widgets.get(item)
        if widget is not None:
            return float(widget.value())
        return super(VectorSpinBox, self).__getAttribute__(item)

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
        self.mainLayout.setSpacing(uiconstants.SPACING)
        self.label = QtWidgets.QLabel(label, parent=self)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.mainLayout.addWidget(self.label, 0, 0)
        self.mainLayout.addItem(spacerItem, 1, 0)
        self._widgets = OrderedDict()
        axislabels = ("X", "Y", "Z")
        for i, c in enumerate(matrix):
            vec = VectorSpinBox(label="", value=c, min=min[i], max=max[i], axis=axislabels, parent=self)
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
        self.layout.setContentsMargins(*uiconstants.MARGINS)
        self.layout.setSpacing(uiconstants.SPACING)
        # self.group.setLayout(self.layout)
        self.translationVec = VectorSpinBox("Translation:", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        self.rotationVec = VectorSpinBox("Rotation:", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        self.scaleVec = VectorSpinBox("Scale:", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        self.rotationOrderBox = ComboBoxSearchable("RotationOrder:", Transformation.rotOrders, parent=self)
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


class RadioButtonGroup(QtWidgets.QWidget):
    """Creates a horizontal group of radio buttons

    Build widget example:
        self.radioWidget = layouts.RadioButtonGroup(radioList=radioNameList, toolTipList=radioToolTipList,
                                                            default=0, parent=parent)

    Query the checked selection example:
        nameChecked = radioWidget.getChecked().text()  # returns the text name of the checked item
        numberChecked = radioWidget.getCheckedIndex() # returns the list number of the checked item

    Return Selection Changed example:
        radioWidget.toggled.connect(self.doSomething)
    """
    toggled = QtCore.Signal(int)

    def __init__(self, radioList=None, toolTipList=None, default=0, parent=None, vertical=False):
        """Horizontal group of radio buttons

        :param radioList: a list of radio button names (strings)
        :type radioList: list
        :param default: the default button to be checked as on, starts at 0 matching the list
        :type default: int
        :param parent: the parent widget
        :type parent: obj
        """
        super(RadioButtonGroup, self).__init__(parent=parent)
        # todo: STYLESHEET needs to be in the stylesheet and not hardcoded
        # rgb(27, 27, 27) is the main color of the unchecked button
        # rgb(45, 45, 45) is the background color of the window, unchecked has no icon
        indicatorWH = utils.dpiScale(14)
        uncheckedWH = utils.dpiScale(10)
        borderRadius = utils.dpiScale(7)
        borderPx = utils.dpiScale(2)
        styleSheetF = "QRadioButton::indicator {0}" \
                      "width: {2}px; " \
                      "height: {2}px;{1}" \
                      "QRadioButton::indicator:unchecked " \
                      "{0}background: rgb(27, 27, 27); " \
                      "width: {3}px; " \
                      "height: {3}px;" \
                      "border-radius: {4}px; " \
                      "border: {5}px solid rgb(45, 45, 45){1}".format("{", "}", indicatorWH, uncheckedWH,
                                                                      borderRadius, borderPx)
        if radioList is None:
            radioList = []
        self.radioButtons = []
        self.group = QtWidgets.QButtonGroup(parent=self)
        if not vertical:
            radioLayout = QtWidgets.QHBoxLayout()
        else:
            radioLayout = QtWidgets.QVBoxLayout()
        for i, radioName in enumerate(radioList):
            newRadio = QtWidgets.QRadioButton(radioName, self)
            newRadio.setStyleSheet(styleSheetF)
            if toolTipList:
                newRadio.setToolTip(toolTipList[i])
            self.group.addButton(newRadio)
            radioLayout.addWidget(newRadio)
            self.radioButtons.append(newRadio)
        if default is not None and default < len(self.radioButtons):
            self.radioButtons[default].setChecked(True)
        self.group.buttonClicked.connect(self.toggled.emit)
        self.setLayout(radioLayout)

    def getChecked(self):
        """ Returns the widget that is checked

        :return widget: the widget that is checked
        :type widget: QtWidgets.QRadioButton()
        """
        for radioBtn in self.radioButtons:
            if radioBtn.isChecked():
                return radioBtn

    def getCheckedIndex(self):
        """ Returns the widget number that is checked

        :return numberChecked: the widget list number that is checked
        :type numberChecked: int
        """
        for i, radioBtn in enumerate(self.radioButtons):
            if radioBtn.isChecked():
                return i


class labelColorBtn(QtWidgets.QWidget):
    """Creates a label and a color button (with no text) which opens a QT color picker,
    returns both rgb (0-255) and rgbF (0-1.0) values
    """
    colorChanged = QtCore.Signal(object)

    def __init__(self, label="Color:", initialRgbColor=None, initialRgbColorF=None, contentsMargins=(0, 0, 0, 0),
                 parent=None, labelWeight=1, colorWeight=1, colorWidth=None):
        """Initialize variables

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
        self.layout = HBoxLayout(parent=None, margins=utils.marginsDpiScale(*contentsMargins),
                                 spacing=utils.dpiScale(uiconstants.SPACING))
        self.layout.addWidget(QtWidgets.QLabel(label, parent=self), labelWeight)
        self.colorPickerBtn = QtWidgets.QPushButton("", parent=self)
        # use initialRgbColor (255 range) or initialRgbColorF (float range 0-1)
        # if no color given then default to red
        self.storedRgbColor = initialRgbColor or tuple([i * 255 for i in initialRgbColorF]) or tuple([255, 0, 0])
        self.colorPickerBtn.setStyleSheet("background-color: rgb{}".format(str(self.storedRgbColor)))
        if colorWidth:
            self.colorPickerBtn.setFixedWidth(colorWidth)
        self.layout.addWidget(self.colorPickerBtn, colorWeight)
        self.setLayout(self.layout)
        self.connections()

    def setColor(self, rgbList):
        """Sets the color of the button as per a rgb list in 0-255 range

        :param rgbList: r g b color in 255 range eg [255, 0, 0]
        :type rgbList: list
        """
        # if the user hits cancel the returned color is invalid, so don't update
        self.storedRgbColor = rgbList
        color = QtGui.QColor(self.storedRgbColor[0], self.storedRgbColor[1], self.storedRgbColor[2], 255)
        self.colorPickerBtn.setStyleSheet("background-color: {}".format(color.name()))

    def setColorSrgb(self, rgbList):
        """Sets the color of the button as per a rgb list in 0-1 range

        :param rgbList: r g b color in 255 range eg [1.0, 0.0, 0.0]
        :type rgbList: list
        """
        self.setColor([color*255 for color in rgbList])

    def pickColor(self):
        """Opens the color picker window
        If ok is pressed then the new color is returned in 0-255 ranges Eg (128, 255, 12)
        If Cancel is pressed the color is invalid and nothing happens
        """
        initialPickColor = QtGui.QColor(self.storedRgbColor[0], self.storedRgbColor[1], self.storedRgbColor[2], 255)
        color = QtWidgets.QColorDialog.getColor(initialPickColor)  # expects 255 range
        if QtGui.QColor.isValid(color):
            rgbList = (color.getRgb())[0:3]
            self.setColor(rgbList)
            self.colorChanged.emit(color)

    def rgbColor(self):
        """returns rgb tuple with 0-255 ranges Eg (128, 255, 12)
        """
        return self.storedRgbColor

    def rgbColorF(self):
        """returns rgb tuple with 0-1.0 float ranges Eg (1.0, .5, .6666)
        """
        return tuple(float(i)/255 for i in self.storedRgbColor)

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
        # todo: STYLSHEET, cleanup this class, remove margin hardcoding and colors use stylesheet instead
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

        .. code-block::python

            # Ellipsis false will omit the ellipsis (...)
            wgt = ClippedLabel(text="Hello World", ellipsis=False)

            # With triple dot added if the size of the widget is too small
            wgt = ClippedLabel(text="Hello World", ellipsis=True)

            # Use it like any other QLabel
            layout = QtWidgets.QHBoxWidget()
            layout.addWidget(wgt)

        :param text:
        :param width:
        :param parent:
        :param ellipsis: True to show ellipsis, false for otherwise
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


def HBoxLayout(parent=None, margins=(0, 0, 0, 0), spacing=uiconstants.SREG):
    """One liner for QtWidgets.QHBoxLayout() to make it easier to create an easy Horizontal Box layout
    DPI (4k) is handled here
    Defaults use regular spacing and no margins

    :param margins:  override the margins with this value
    :type margins: tuple
    :param spacing: override the spacing with this pixel value
    :type spacing: int
    """
    zooQHBoxLayout = QtWidgets.QHBoxLayout(parent)
    zooQHBoxLayout.setContentsMargins(*utils.marginsDpiScale(*margins))
    zooQHBoxLayout.setSpacing(utils.dpiScale(spacing))
    return zooQHBoxLayout


def VBoxLayout(parent=None, margins=(0, 0, 0, 0), spacing=uiconstants.SREG):
    """One liner for QtWidgets.QVBoxLayout() to make it easier to create an easy Vertical Box layout
    DPI (4k) is handled here
    Defaults use regular spacing and no margins

    :param margins:  override the margins with this value
    :type margins: tuple
    :param spacing: override the spacing with this pixel value
    :type spacing: int
    """
    zooQVBoxLayout = QtWidgets.QVBoxLayout(parent)
    zooQVBoxLayout.setContentsMargins(*utils.marginsDpiScale(*margins))
    zooQVBoxLayout.setSpacing(utils.dpiScale(spacing))
    return zooQVBoxLayout


def GridLayout(parent=None, margins=(0, 0, 0, 0), spacing=uiconstants.SREG, columnMinWidth=None):
    """One liner for QtWidgets.QGridLayout() to make it easier to create an easy Grid layout
    DPI (4k) is handled here
    Defaults use regular spacing and no margins

    :param margins:  override the margins with this value
    :type margins: tuple
    :param spacing: override the spacing with this pixel value
    :type spacing: int
    :param columnMinWidth: option for one column number then it's min width, use obj.setColumnMinimumWidth for more
    :type columnMinWidth: tuple
    """
    zooGridLayout = QtWidgets.QGridLayout()
    zooGridLayout.setContentsMargins(*utils.marginsDpiScale(*margins))
    zooGridLayout.setSpacing(utils.dpiScale(spacing))
    if columnMinWidth:  # column number then the width in pixels
        zooGridLayout.setColumnMinimumWidth(columnMinWidth[0], utils.dpiScale(columnMinWidth[1]))
    return zooGridLayout


def Spacer(width, height, hMin=QtWidgets.QSizePolicy.Minimum, vMin=QtWidgets.QSizePolicy.Minimum):
    """creates an expanding spacer (empty area) with easy options.  DPI auto handled

    Size Policies are
    https://srinikom.github.io/pyside-docs/PySide/QtGui/QSizePolicy.html#PySide.QtGui.PySide.QtGui.QSizePolicy.Policy
        QtWidgets.QSizePolicy.Fixed -  never grows or shrinks
        QtWidgets.QSizePolicy.Minimum - no advantage being larger
        QtWidgets.QSizePolicy.Maximum - no advantage being smaller
        QtWidgets.QSizePolicy.Preferred - The sizeHint() is best, but the widget can be shrunk/expanded
        QtWidgets.QSizePolicy.Expanding -  but the widget can be shrunk or make use of extra space
        QtWidgets.QSizePolicy.MinimumExpanding - The sizeHint() is minimal, and sufficient
        QtWidgets.QSizePolicy.Ignored - The sizeHint() is ignored. Will get as much space as possible

    :param width: width of the spacer in pixels, DPI is auto handled
    :type width: int
    :param height: height of the spacer in pixels, DPI is auto handled
    :type height: int
    :param hMin: height of the spacer in pixels, DPI is auto handled
    :type hMin: PySide.QtGui.QSizePolicy.Policy
    :param vMin: vertical minimum
    :type vMin: PySide.QtGui.QSizePolicy.Policy
    :return spacerItem: item returned, ie the spacerItem
    :rtype spacerItem: object
    """
    return QtWidgets.QSpacerItem(utils.dpiScale(width), utils.dpiScale(height), hMin, vMin)

