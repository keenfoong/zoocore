from collections import OrderedDict
from functools import partial

from qt import QtWidgets, QtCore, QtGui

from zoo.libs import iconlib
from zoo.libs.pyqt import utils
from zoo.libs.pyqt import uiconstants as uic
from zoo.libs.pyqt.extended import combobox
from zoo.libs.pyqt.widgets import frame


def Label(name, parent, toolTip="", upper=False, bold=False, enableMenu=True):
    """One liner for labels and tooltip

    :param name: name of the text label
    :type name: str
    :param parent: the qt parent
    :type parent: class
    :param toolTip: the tool tip message on mouse over hover, extra info
    :type toolTip: str
    :param upper: make the label all caps
    :type upper: bool
    :param bold: make the label font bold
    :type bold: bool
    :return lbl: the QT QLabel widget
    :rtype lbl: QWidget.QLabel
    """
    if upper:
        name = name.upper()
    if enableMenu:
        lbl = ExtendedLabelMenu(name, parent=parent)
    else:
        lbl = QtWidgets.QLabel(name, parent=parent)
    lbl.setToolTip(toolTip)
    if bold:
        lbl.setStyleSheet("font: bold;")

    return lbl


def TextEdit(text="", placeholderText="", parent=None, toolTip="", editWidth=None, minimumHeight=None,
             maximumHeight=None, fixedWidth=None):
    """Creates a simple textbox (QTextEdit) which can have multiple lines unlike a (LineEdit)
    Handles DPI for min and max height

    :param text: is the default text in the text box
    :type text: str or float or int
    :param placeholderText will be greyed out text in the text box, overrides text=""
    :type placeholderText: str or float or int
    :param parent: the qt parent
    :type parent: class
    :param toolTip: the tool tip message on mouse over hover, extra info
    :type toolTip: str
    :param editWidth: the width of the textbox in pixels optional, None is ignored
    :type editWidth: int
    :param minimumHeight: the minimum height for the text box in pixels, optional, None is ignored
    :type minimumHeight: int
    :param maximumHeight: the maximum height for the text box in pixels, optional, None is ignored
    :type maximumHeight: int
    :param fixedWidth: the width (max and min) of the text box
    :type fixedWidth: int
    :return textEdit: the QT QTextEdit widget
    :rtype textEdit: QWidget.QTextEdit
    """
    textEdit = QtWidgets.QTextEdit(parent=parent)
    utils.setStylesheetObjectName(textEdit, "textEditForced")  # TODO: might be removed once stack widget fixed
    if minimumHeight:
        textEdit.setMinimumHeight(utils.dpiScale(minimumHeight))
    if maximumHeight:
        textEdit.setMaximumHeight(utils.dpiScale(maximumHeight))
    if fixedWidth:
        textEdit.setFixedWidth(utils.dpiScale(fixedWidth))
    textEdit.setPlaceholderText(placeholderText)
    textEdit.setText(text)
    textEdit.setToolTip(toolTip)

    return textEdit


class ExtendedLineEdit(QtWidgets.QLineEdit):
    textModified = QtCore.Signal()

    def __init__(self, parent=None):
        super(ExtendedLineEdit, self).__init__(parent)
        self.editingFinished.connect(self._handleEditingFinished)
        self.textChanged.connect(self._handleTextChanged)
        self.returnPressed.connect(self._handleReturnPressed)
        self._before = ""

    def _getBeforeAfter(self):
        """Returns the before state and the after

        Checks if the textbox is a float, if so compare the numbers to account for irrelevant decimal differences"""
        if type(self.validator()) == QtGui.QDoubleValidator:  # float
            return float(self._before), float(self.text())
        else:
            return self._before, self.text()

    def _handleTextChanged(self, text):
        """If text has changed update self._before
        """
        if not self.hasFocus():
            self._before = text

    def _handleEditingFinished(self):
        """if text has changed and editingFinished emit textModified
        """
        before, after = self._getBeforeAfter()
        if before != after:
            self._before = after
            self.textModified.emit()

    def _handleReturnPressed(self):
        """if text hasn't changed and returnPressed emit textModified
        """
        before, after = self._getBeforeAfter()
        if before == after:
            self.textModified.emit()


def LineEdit(text="", placeholder="", parent=None, toolTip="", editWidth=None, inputMode="string", fixedWidth=None,
             enableMenu=True):
    """Creates a simple textbox (QLineEdit)

    :param text: is the default text in the text box
    :type text: str or float or int
    :param placeholder will be greyed out text in the text box, overrides text=""
    :type placeholder: str or float or int
    :param parent: the qt parent
    :type parent: class
    :param toolTip: the tool tip message on mouse over hover, extra info
    :type toolTip: str
    :param editWidth: the width of the textbox in pixels optional, None is ignored
    :type editWidth: int
    :param inputMode: restrict the user to this data entry, "string" text, "float" decimal or "int" no decimal
    :type inputMode: str
    :param enableMenu: If True (default) uses ExtendedLineEditMenu, right/middle/left click menus can be added
    :type enableMenu: bool
    :return textBox: the QT QLabel widget
    :rtype textBox: QWidget.QLabel
    """
    if enableMenu:
        textBox = ExtendedLineEditMenu(parent=parent)
    else:
        textBox = ExtendedLineEdit(parent=parent)
    utils.setStylesheetObjectName(textBox, "lineEditForced")  # TODO: should be removed once stack widget fixed
    if inputMode == "float":  # float restricts to only numerical decimal point text entry
        textBox.setValidator(QtGui.QDoubleValidator())
    elif inputMode == "int":  # int restricts to numerical text entry, no decimal places
        textBox.setValidator(QtGui.QIntValidator())
    if editWidth:  # limit the width of the textbox
        textBox.setFixedWidth(utils.dpiScale(editWidth))
    if fixedWidth:
        textBox.setFixedWidth(utils.dpiScale(fixedWidth))
    textBox.setPlaceholderText(str(placeholder))
    textBox.setText(str(text))
    textBox.setToolTip(toolTip)
    return textBox


class StringEdit(QtWidgets.QWidget):
    textChanged = QtCore.Signal(str)
    buttonClicked = QtCore.Signal()
    editingFinished = QtCore.Signal()

    def __init__(self, label="", editText="", editPlaceholder="", buttonText=None, parent=None, editWidth=None,
                 labelRatio=1, btnRatio=1, editRatio=1, toolTip="", inputMode="string",
                 orientation=QtCore.Qt.Horizontal, enableMenu=True):
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
        :param orientation: the orientation of the box layout QtCore.Qt.Horizontal HBox QtCore.Qt.Vertical VBox
        :type orientation: bool
        :param enableMenu: If True (default) uses ExtendedLineEditMenu, right/middle/left click menus can be added
        :type enableMenu: bool
        :return StringEdit: returns the class with various options, see the methods
        :rtype StringEdit: QWidget
        """
        super(StringEdit, self).__init__(parent=parent)
        self.enableMenu = enableMenu
        self.QLineEditBool = True
        if orientation == QtCore.Qt.Horizontal:
            self.layout = hBoxLayout(parent, (0, 0, 0, 0), spacing=uic.SREG)
        else:
            self.layout = vBoxLayout(parent, (0, 0, 0, 0), spacing=uic.SREG)
        self.edit = LineEdit(editText, editPlaceholder, parent, toolTip, editWidth, inputMode, enableMenu=enableMenu)
        if label:
            self.label = Label(label, parent, toolTip)
            self.layout.addWidget(self.label, labelRatio)
        self.layout.addWidget(self.edit, editRatio)
        self.buttonText = buttonText
        if self.buttonText:
            # todo button connections should be added from this class (connections)
            self.btn = QtWidgets.QPushButton(buttonText, parent)
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
        self.label.setDisabled(state)

    def setText(self, value):
        """Change the text at any time"""
        self.edit.setText(value)

    def setLabelFixedWidth(self, width):
        """Set the fixed width of the label"""
        self.label.setFixedWidth(utils.dpiScale(width))

    def setTxtFixedWidth(self, width):
        """Set the fixed width of the lineEdit"""
        self.edit.setFixedWidth(utils.dpiScale(width))

    def text(self):
        """get the text of self.edit"""
        return self.edit.text()

    def clearFocus(self):
        self.edit.clearFocus()

    # ----------
    # MENUS
    # ----------
    def setMenu(self, menu, modeList=None, mouseButton=QtCore.Qt.RightButton):
        """Add the left/middle/right click menu by passing in a QMenu

        If a modeList is passed in then create/reset the menu to the modeList:

            [("icon1", "menuName1"), ("icon2", "menuName2")]

        If no modelist the menu won't change

        :param menu: the Qt menu to show on middle click
        :type menu: QtWidgets.QMenu
        :param modeList: a list of menu modes (tuples) eg [("icon1", "menuName1"), ("icon2", "menuName2")]
        :type modeList: list(tuple(str))
        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        if mouseButton != QtCore.Qt.LeftButton:  # don't create an edit menu if left mouse button menu
            self.edit.setMenu(menu, mouseButton=mouseButton)
        # only add the action list (menu items) to the label, as the line edit uses the same menu
        self.label.setMenu(menu, modeList=modeList, mouseButton=mouseButton)

    def addActionList(self, modes, mouseButton=QtCore.Qt.RightButton):
        """resets the appropriate mouse click menu with the incoming modes

            modeList: [("icon1", "menuName1"), ("icon2", "menuName2"), ("icon3", "menuName3")]

        resets the lists and menus:

            self.menuIconList: ["icon1", "icon2", "icon3"]
            self.menuIconList: ["menuName1", "menuName2", "menuName3"]

        :param modes: a list of menu modes (tuples) eg [("icon1", "menuName1"), ("icon2", "menuName2")]
        :type modes: list(tuple(str))
        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        # only add the action list (menu items) to the label, as the line edit uses the same menu
        self.label.addActionList(modes, mouseButton=mouseButton)


class ComboBoxSearchable(QtWidgets.QWidget):
    itemChanged = QtCore.Signal(int, str)

    def __init__(self, label="", items=(), parent=None, labelRatio=None, boxRatio=None, toolTip="", setIndex=0,
                 sortAlphabetically=False):
        """Creates a searchable combo box (drop down menu) with a label

        :param label: the label of the combobox
        :type label: str
        :param items: the item list of the combobox
        :type items: tuple
        :param parent: the qt parent
        :type parent: class
        """
        # TODO needs to stylesheet the lineEdit text entry
        super(ComboBoxSearchable, self).__init__(parent=parent)
        layout = hBoxLayout(parent=None, margins=(0, 0, 0, 0),
                            spacing=utils.dpiScale(uic.SPACING))  # margins kwarg should be added
        self.box = combobox.ExtendedComboBox(items, parent)
        self.box.setToolTip(toolTip)
        if sortAlphabetically:
            items = list(items)
            self.box.InsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
            items.sort(key=str.lower)  # sort list alphabetically case insensitive
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
        self.setLayout(layout)

        self.box.currentIndexChanged.connect(self.onItemChanged)

    def __getattr__(self, item):
        if hasattr(self.box, item):
            return getattr(self.box, item)
        super(ComboBoxSearchable, self).__getAttribute__(item)

    def clear(self):
        """ Clear all items

        :return:
        """
        self.box.clear()

    def addItems(self, items, sortAlphabetically=False):
        """ Add items to combobox

        :param items:
        :param sortAlphabetically:
        :return:
        """
        self.box.addItems(items)
        if sortAlphabetically:
            self.themeBox.model().sort(0)

    def addItem(self, item, sortAlphabetically=False):
        """adds an entry to the combo box

        :param item: the name to add to the combo box
        :type item: str
        :param sortAlphabetically: sorts the full combo box alphabetically after adding
        :type sortAlphabetically: bool
        """
        self.box.addItem(item)
        if sortAlphabetically:
            self.themeBox.model().sort(0)

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

        :param text: Text to search and switch the comboxBox to
        :type text: str
        """
        index = self.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)

    def setToTextQuiet(self, text):
        """Sets the index based on the text and stops comboBox from emitting signals while being changed

        :param text: Text to search and switch the comboxBox to
        :type text: str
        """
        self.box.blockSignals(True)
        self.setToText(self, text)
        self.box.blockSignals(False)

    def setIndex(self, index):
        """Sets the combo box to the current index number

        :param index: Sets the combo box to the current index
        :type index: int
        """
        self.box.setCurrentIndex(index)

    def setIndexQuiet(self, index):
        """Sets the combo box to the current index number, stops comboBox from emitting signals while being changed

        :param index: the index item number of the comboBox
        :type index: int
        """
        self.box.blockSignals(True)
        self.box.setCurrentIndex(index)
        self.box.blockSignals(False)

    def setLabelFixedWidth(self, width):
        """Set the fixed width of the label

        :param width: the width in pixels, DPI is handled
        :type width: int
        """
        self.label.setFixedWidth(utils.dpiScale(width))

    def setBoxFixedWidth(self, width):
        """Set the fixed width of the lineEdit

        :param width: the width in pixels, DPI is handled
        :type width: int
        """
        self.box.setFixedWidth(utils.dpiScale(width))


def comboBox(items=(), parent=None, toolTip="", setIndex=0, sortAlphabetically=False):
    """Simple qComboBox with no label

    :param items: the item list of the combobox
    :type items: list
    :param parent: the qt parent
    :type parent: object
    :param toolTip: the tooltip info to display with mouse hover
    :type toolTip: str
    :param setIndex: set the combo box value as an int - 0 is the first value, 1 is the second
    :type setIndex: int
    :return comboBx: the QComboBox Qt widget
    :type comboBx: QComboBox
    """
    comboBx = QtWidgets.QComboBox(parent)
    if sortAlphabetically:
        comboBx.InsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        if items:
            items = list(items)
            items = [x.encode('UTF8') for x in items]  # if unicode convert to str
            items.sort(key=str.lower)  # sort list alphabetically case insensitive
    comboBx.addItems(items)
    comboBx.setToolTip(toolTip)
    if setIndex:
        comboBx.setCurrentIndex(setIndex)
    return comboBx


class ComboBoxRegular(QtWidgets.QWidget):
    """Creates a regular "not searchable" combo box (drop down menu) with a label
    """
    itemChanged = QtCore.Signal(int, str)

    def __init__(self, label="", items=(), parent=None, labelRatio=None, boxRatio=None, toolTip="", setIndex=0,
                 sortAlphabetically=False):
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

        self.box = comboBox(items=items, parent=parent, toolTip=toolTip, setIndex=setIndex,
                            sortAlphabetically=sortAlphabetically)

        layout = hBoxLayout(parent=None, margins=utils.marginsDpiScale(0, 0, 0, 0),
                            spacing=utils.dpiScale(uic.SREG))  # margins kwarg should be added
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

    def addItem(self, item, sortAlphabetically=False):
        """adds an entry to the combo box

        :param item: the name to add to the combo box
        :type item: str
        :param sortAlphabetically: sorts the full combo box alphabetically after adding
        :type sortAlphabetically: bool
        """
        self.box.addItem(item)
        if sortAlphabetically:
            self.themeBox.model().sort(0)

    def setItemData(self, index, value):
        """Sets the data role for the item on the given index in the combobox to the specified value.
        Good for metadata assigned to the name

        :param index: the index to assign the value
        :type index: int
        :param value: the value to assign, can be any object or string etc
        :type value: object
        """
        self.box.setItemData(index, value)

    def setToText(self, text):
        """Sets the index based on the text

        :param text: Text to search and switch the comboxBox to
        :type text: str
        """
        index = self.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.box.setCurrentIndex(index)

    def setToTextQuiet(self, text):
        """Sets the index based on the text and stops comboBox from emitting signals while being changed

        :param text: Text to search and switch the comboxBox to
        :type text: str
        """
        self.box.blockSignals(True)
        self.setToText(self, text)
        self.box.blockSignals(False)

    def setIndex(self, index):
        """Sets the combo box to the current index number

        :param index: Sets the combo box to the current index
        :type index: int
        """
        self.box.setCurrentIndex(index)

    def setIndexQuiet(self, index):
        """Sets the combo box to the current index number, stops comboBox from emitting signals while being changed

        :param index: the index item number of the comboBox
        :type index: int
        """
        self.box.blockSignals(True)
        self.box.setCurrentIndex(index)
        self.box.blockSignals(False)

    def removeItemByText(self, text):
        """removes the index based on the text from the combo box (box.removeItem)

        :param text: Text to search and delete it's entire entry from the combo box (removeItem)
        :type text: str
        """
        index = self.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.box.removeItem(index)

    def setLabelFixedWidth(self, width):
        """Set the fixed width of the label"""
        self.label.setFixedWidth(utils.dpiScale(width))

    def setBoxFixedWidth(self, width):
        """Set the fixed width of the lineEdit"""
        self.box.setFixedWidth(utils.dpiScale(width))


def CheckBoxRegular(label="", setChecked=False, parent=None, toolTip="", enableMenu=True):
    """Creates a regular QCheckbox check box (on off) with extra simple options

    Uses the ExtendedCheckboxMenu so left/right/middle click menus can be added

    Set enableMenu to True if you'd like to add menus to the checkbox (uses ExtendedCheckboxMenu)

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
    if enableMenu:
        box = ExtendedCheckboxMenu(label, parent=parent)
    else:
        box = QtWidgets.QCheckBox(label, parent=parent)
    box.setToolTip(toolTip)
    if setChecked:
        box.setChecked(setChecked)
    return box


class VectorLineEdit(QtWidgets.QWidget):
    """A label with multiple QLineEdits (text boxes), no spin boxes usually for x y z numeric input
    use inputMode="float" to restrict the data entry to decimal numbers
    """
    textChanged = QtCore.Signal(tuple)
    textModified = QtCore.Signal(tuple)

    def __init__(self, label, value, axis=("x", "y", "z"), parent=None, toolTip="", inputMode="float", labelRatio=1,
                 editRatio=1, spacing=uic.SREG):
        """A label with multiple QLineEdits (text boxes), no spin boxes usually for x y z numeric input
        use inputMode="float" to restrict the data entry to decimal numbers

        :param label: the label for the vector eg. translate, if the label is None or "" then it will be excluded
        :type label: str
        :param value: n floats corresponding with axis param
        :type value: tuple(float)
        :param axis: every axis ("x", "y", "z") or ("x", "y", "z", "w")
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
        self.mainLayout = hBoxLayout(parent, (0, 0, 0, 0), spacing)
        self.axis = axis
        if label:
            self.label = QtWidgets.QLabel(label, parent=self)
            self.mainLayout.addWidget(self.label, labelRatio)
        self._widgets = OrderedDict()
        vectorEditLayout = hBoxLayout(parent, (0, 0, 0, 0), spacing)
        for i, v in enumerate(axis):
            edit = LineEdit(text=value[i], placeholder="", parent=parent, toolTip=toolTip, inputMode=inputMode)
            # edit.setObjectName("".join([label, v]))  # might not need a label name?  Leave this line in case

            edit.textModified.connect(self._onTextModified)
            edit.textChanged.connect(self._onTextChanged)
            self._widgets[v] = edit
            vectorEditLayout.addWidget(edit)
        self.mainLayout.addLayout(vectorEditLayout, editRatio)
        self.setLayout(self.mainLayout)

    def _onTextChanged(self):
        """updates the text, should also update the dict
        """
        valueList = [self._widgets[axis].text() for axis in self._widgets]
        self.textChanged.emit(tuple(valueList))

    def _onTextModified(self):
        """updates the text, should also update the dict
        """
        valueList = [self._widgets[axis].text() for axis in self._widgets]
        self.textModified.emit(tuple(valueList))

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
        valueList = [self._widgets[axis].text() for axis in self._widgets]
        if type(self._widgets[self.axis[0]].validator()) == QtGui.QDoubleValidator:  # float
            return [float(value) for value in valueList]
        elif type(self._widgets[self.axis[0]].validator()) == QtGui.QIntValidator:  # int:
            return [int(value) for value in valueList]
        return tuple(valueList)

    def setValue(self, value):
        """Sets the text values of all the QLineEdits, can be strings floats or ints depending on the inputMode

        :param value: the value of all text boxes, as a list of strings (or floats, ints depending on inputMode)
        :type value: tuple
        """
        # get the widgets in order
        keys = self._widgets.keys()
        for i, v in enumerate(value):
            self._widgets[keys[i]].setText(str(v))

    def setLabelFixedWidth(self, width):
        """Set the fixed width of the label"""
        self.label.setFixedWidth(utils.dpiScale(width))

    def hideLineEdit(self, axisInt):
        """hides one of the lineEdits from by index from self.axis list

        :param axisInt: the index of the lineEdit to hide
        :type axisInt: int
        """
        self._widgets[self.axis[axisInt]].hide()

    def showLineEdit(self, axisInt):
        """shows one of the lineEdits from by index from self.axis list

        :param axisInt: the index of the lineEdit to hide
        :type axisInt: int
        """
        self._widgets[self.axis[axisInt]].show()



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
        self.mainLayout = hBoxLayout(parent, (2, 2, 2, 2), uic.SREG)
        if label:
            self.label = QtWidgets.QLabel(label, parent=self)
            self.mainLayout.addWidget(self.label)
        self._widgets = OrderedDict()

        for i, v in enumerate(axis):
            box = QtWidgets.QDoubleSpinBox(self)
            box.setSingleStep(step)
            box.setObjectName("".join([label, v]))
            box.setRange(min, max)
            box.setValue(value[i])
            box.setDecimals(setDecimals)
            box.valueChanged.connect(self.onValueChanged)
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
        self.mainLayout.setSpacing(uic.SPACING)
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
        self.layout.setContentsMargins(*uic.MARGINS)
        self.layout.setSpacing(uic.SPACING)
        # self.group.setLayout(self.layout)
        self.translationVec = VectorSpinBox("Translation:", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis,
                                            parent=self)
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
        self.layout = hBoxLayout(parent=None, margins=utils.marginsDpiScale(*contentsMargins),
                                 spacing=utils.dpiScale(uic.SPACING))
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

    def setColorSrgbInt(self, rgbList):
        """Sets the color of the button as per a rgb list in 0-255 range

        :param rgbList: r g b color in 255 range eg [255, 0, 0]
        :type rgbList: list
        """
        # if the user hits cancel the returned color is invalid, so don't update
        self.storedRgbColor = rgbList
        color = QtGui.QColor(self.storedRgbColor[0], self.storedRgbColor[1], self.storedRgbColor[2], 255)
        self.colorPickerBtn.setStyleSheet("background-color: {}".format(color.name()))

    def setColorSrgbFloat(self, rgbList):
        """Sets the color of the button as per a rgb list in 0-1 range, colors are not rounded

        :param rgbList: r g b color in float range eg [1.0, 0.0, 0.0]
        :type rgbList: list
        """
        self.setColorSrgbInt([color * 255 for color in rgbList])

    def pickColor(self):
        """Opens the color picker window
        If ok is pressed then the new color is returned in 0-255 ranges Eg (128, 255, 12)
        If Cancel is pressed the color is invalid and nothing happens
        """
        initialPickColor = QtGui.QColor(self.storedRgbColor[0], self.storedRgbColor[1], self.storedRgbColor[2], 255)
        color = QtWidgets.QColorDialog.getColor(initialPickColor)  # expects 255 range
        if QtGui.QColor.isValid(color):
            rgbList = (color.getRgb())[0:3]
            self.setColorSrgbInt(rgbList)
            self.colorChanged.emit(color)

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
    _collapsedIcon = iconlib.icon("sortClosed", size=utils.dpiScale(12))
    _expandIcon = iconlib.icon("sortDown", size=utils.dpiScale(12))

    def __init__(self, title, collapsed=False, collapsable=True, contentMargins=uic.MARGINS,
                 contentSpacing=uic.SPACING, parent=None):
        """Collapsable framelayout, similar to Maya's cmds.frameLayout
        Title is inside a bg colored frame layout that can open and collapsed
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
        self.layout = vBoxLayout(parent=parent, margins=(0, 0, 0, 0), spacing=0)
        self.title = title
        self.contentMargins = contentMargins
        self.contentSpacing = contentSpacing
        self.collapsable = collapsable
        self.collapsed = collapsed
        if not collapsable:  # if not collapsable must be open
            self.collapsed = False
        self.initUi()
        self.setLayout(self.layout)
        self.connections()
        utils.setStylesheetObjectName(self.titleFrame, "collapse")

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
        self.titleFrame = frame.QFrame(parent=self)
        self.titleFrame.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = hBoxLayout(self.titleFrame, margins=(0, 0, 0, 0))
        # the icon
        self.iconButton = QtWidgets.QToolButton(parent=self)

        if self.collapsed:
            self.iconButton.setIcon(self._collapsedIcon)
        else:
            self.iconButton.setIcon(self._expandIcon)
        self.iconButton.setContentsMargins(0, 0, 0, 0)
        self.titleLabel = Label(self.title, parent=self, bold=True)
        self.titleLabel.setContentsMargins(0, 0, 0, 0)
        spacerItem = QtWidgets.QSpacerItem(10, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # add to horizontal layout
        self.horizontalLayout.addWidget(self.iconButton)
        self.horizontalLayout.addWidget(self.titleLabel)
        self.horizontalLayout.addItem(spacerItem)

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
        self.hiderLayout = vBoxLayout(self.widgetHider, margins=self.contentMargins, spacing=self.contentSpacing)
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


def hBoxLayout(parent=None, margins=(0, 0, 0, 0), spacing=uic.SREG):
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


def vBoxLayout(parent=None, margins=(0, 0, 0, 0), spacing=uic.SREG):
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


def GridLayout(parent=None, margins=(0, 0, 0, 0), spacing=uic.SREG, columnMinWidth=None, vSpacing=None,
               hSpacing=None):
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
    zooGridLayout = QtWidgets.QGridLayout(parent)
    zooGridLayout.setContentsMargins(*utils.marginsDpiScale(*margins))
    if not vSpacing and not hSpacing:
        zooGridLayout.setHorizontalSpacing(utils.dpiScale(spacing))
        zooGridLayout.setVerticalSpacing(utils.dpiScale(spacing))
    elif vSpacing and not hSpacing:
        zooGridLayout.setHorizontalSpacing(utils.dpiScale(hSpacing))
        zooGridLayout.setVerticalSpacing(utils.dpiScale(vSpacing))
    elif hSpacing and not vSpacing:
        zooGridLayout.setHorizontalSpacing(utils.dpiScale(hSpacing))
        zooGridLayout.setVerticalSpacing(utils.dpiScale(spacing))
    else:
        zooGridLayout.setHorizontalSpacing(utils.dpiScale(hSpacing))
        zooGridLayout.setVerticalSpacing(utils.dpiScale(vSpacing))
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


def FileDialog_directory(windowName="", parent="", defaultPath=""):
    """simple function for QFileDialog.getExistingDirectory, a window popup that searches for a directory

    Browses for a directory with a fileDialog window and returns the selected directory

    :param windowName: The name of the fileDialog window
    :type windowName: str
    :param parent: The parent widget
    :type parent: Qt.widget
    :param defaultPath: The default directory path, where to open the fileDialog window
    :type defaultPath: str
    :return directoryPath: The selected full directory path
    :rtype directoryPath: str
    """
    directoryPath = str(QtWidgets.QFileDialog.getExistingDirectory(parent, windowName, defaultPath))
    if not directoryPath:
        return
    return directoryPath


def MessageBox_ok(windowName="Confirm", parent="", message="Proceed?"):
    """simple function for ok/cancel QMessageBox.question, a window popup that with ok/cancel buttons

    :param windowName: The name of the ok/cancel window
    :type windowName: str
    :param parent: The parent widget
    :type parent: Qt.widget
    :param message: The message to ask the user
    :type message: str
    :return okPressed: True if the Ok button was pressed, False if cancelled
    :rtype okPressed: bool
    """
    result = QtWidgets.QMessageBox.question(parent, windowName, message,
                                            QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
    if result == QtWidgets.QMessageBox.Ok:
        return True
    return False


def InputDialog(windowName="Add Name", textValue="", parent="", message="Rename?"):
    """Opens a simple QT window that locks the program asking the user to input a string into a text box

    Useful for renaming etc.

    :param windowName: The name of the ok/cancel window
    :type windowName: str
    :param textValue: The initial text in the textbox, eg. The name to be renamed
    :type textValue: str
    :param parent: The parent widget
    :type parent: Qt.widget
    :param message: The message to ask the user
    :type message: str
    :return newTextValue: The new text name entered
    :rtype newTextValue: str
    """
    dialog = QtWidgets.QInputDialog(parent)
    dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
    dialog.setTextValue(textValue)
    dialog.setWindowTitle(windowName)
    dialog.setLabelText(message)
    dialog.resize(utils.dpiScale(270), utils.dpiScale(100))
    ok = dialog.exec_()
    newTextValue = dialog.textValue()
    if not ok:
        return ""
    return newTextValue


class EmbeddedWindow(QtWidgets.QFrame):
    def __init__(self, parent, title, defaultVisibility=True, uppercase=False, closeButton=None):
        """An embedded window is a QFrame widget that appears like a window inside of another ui.

        It is not a window itself, more like a fake window.  It has some simple stylesheeting and a title
        The widget area can also be easily closed and shown again with it's methods

        Assign other widgets to the window by adding to it's QVLayout:
            EmbeddedWindow.propertiesLayout()

        or return the layout with:
            layout = EmbeddedWindow.getLayout()

        :param parent: the parent widget to parent this widget
        :type parent: obj
        :param title: The title of the window, can be changed
        :type title: str
        :param defaultVisibility: Is the embedded window visible on initialize?
        :type defaultVisibility: bool
        :param closeButton: the button (object) used to close the window
        :type closeButton: qt object
        """
        super(EmbeddedWindow, self).__init__(parent)
        self.title = title
        self.parent = parent
        self.uppercase = uppercase
        if closeButton:
            self.hidePropertiesBtn = closeButton
        else:
            self.hidePropertiesBtn = None
        self.setHidden(defaultVisibility)
        self.ui()
        self.connections()

    def ui(self):
        """Create the UI with a title and close icon top right

        self.propertiesLayout is the VLayout where other items can be added to the window. This can also be returned
        with the method getLayout()
        """
        self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        utils.setStylesheetObjectName(self, "embededWindowBG")  # setObjectName with ui update
        self.propertiesLayout = vBoxLayout(self.parent, margins=(uic.WINSIDEPAD, 4, uic.WINSIDEPAD,
                                                                 uic.WINBOTPAD), spacing=uic.SREG)
        self.setLayout(self.propertiesLayout)  # container for stylesheet

        # Title Of the Embedded Window
        propertyTitleLayout = hBoxLayout(self.parent, margins=(0, 0, 0, 0), spacing=uic.SSML)
        self.propertiesLbl = Label(self.title, self.parent, upper=self.uppercase, bold=True)

        propertyTitleLayout.addWidget(self.propertiesLbl, 10)
        if self.hidePropertiesBtn:
            propertyTitleLayout.addWidget(self.hidePropertiesBtn, 1)

        self.propertiesLayout.addLayout(propertyTitleLayout)

    def getLayout(self):
        """Returns the QVLayout where other widgets can be added to the embedded window
        """
        return self.propertiesLayout

    def getTitleLbl(self):
        """Returns the title QLabel widget so that it can be altered
        """
        return self.propertiesLbl

    def getHideButton(self):
        """Returns the hide button so functionality can be assigned to it
        """
        if self.hidePropertiesBtn:
            return self.hidePropertiesBtn

    def setTitle(self, title):
        """Set the title of the embedded window

        :param title: the Title of the embedded window
        :type title: str
        """
        self.propertiesLbl.setText(title)

    def hideEmbedWindow(self):
        """Hide the embedded window
        """
        self.setHidden(True)

    def showEmbedWindow(self):
        """Show the embedded window
        """
        self.setHidden(False)

    def connections(self):
        """UI interaction connections, hide button
        """
        self.hidePropertiesBtn.clicked.connect(self.hideEmbedWindow)


"""
EXTENDED WIDGET MENU CODE
"""


class MenuCreateClickMethods(object):

    def __init__(self):
        """This class can be added to any widget to help add left/right/middle click menus to any widget
        The widget must be extended to support the menus

        To add a menu to a supported extended widget:

            myQMenu =  QtWidgets.QMenu(parent)  # create a menu, need to set it up with menu etc
            zooQtWidget.setMenu(myQMenu, mouseButton=QtCore.Qt.RightButton)  # add menu to the UI with a mouse click

        Or if you are using ExtendedMenu in zoocore_pro, you can easily automatically build the menu items/icons

            myExtMenu =  extendedmenu.ExtendedMenu()  # create an empty zoocore_pro menu (an extended QMenu)
            theMenuModeList = [("menuIcon1", "Menu Item Name 1"),
                                (" menuIcon1  ", " Menu Item Name 2")]  # create the menu names and icons
            zooQtWidget.setMenu(myExtMenu, modeList=theMenuModeList, mouseButton=QtCore.Qt.RightButton)  # add menu

        ExtendedMenu in zoocore_pro can connect when a menu is changed with

            theMenu.menuChanged.connect(runTheMenuFunction)

        Then write a method or function that finds the menu and runs the appropriate code
        (must be a zoocore_pro ExtendedMenu)

            def runTheMenuFunction(self):
                if theMenu.currentMenuItem() == theMenuModeList[0][1]:  # menu item name 1
                    print "first menu item clicked",
                elif theMenu.currentMenuItem() == theMenuModeList[1][1]:  # menu item name 1
                    print "second menu item clicked",

        """
        super(MenuCreateClickMethods, self).__init__()

    def setupMenuClass(self, menuVOffset=20):
        """ The __init__ of this class is not run with multi-inheritance, not sure why, so this is the __init__ code

        :param menuVOffset:  The vertical offset (down) menu drawn from widget top corner.  DPI is handled
        :type menuVOffset: int
        """
        self.menuVOffset = menuVOffset  # offset neg vertical of the menu when drawn, dpi is handled
        # To check of the menu is active
        self.menuActive = {QtCore.Qt.LeftButton: False,
                           QtCore.Qt.MidButton: False,
                           QtCore.Qt.RightButton: False}

        # Store menus into a dictionary
        self.clickMenu = {QtCore.Qt.LeftButton: None,
                          QtCore.Qt.MidButton: None,
                          QtCore.Qt.RightButton: None}

        # Is menu searchable? Not implimented
        self.menuSearchable = {QtCore.Qt.LeftButton: False,
                               QtCore.Qt.MidButton: False,
                               QtCore.Qt.RightButton: False}

    def setMenu(self, menu, modeList=None, mouseButton=QtCore.Qt.RightButton):
        """Add the left/middle/right click menu by passing in a QMenu and assign it to the appropriate mouse click key

        If a modeList is passed in then auto create/reset the menu to the modeList:

            [("icon1", "menuName1"), ("icon2", "menuName2")]

        If no modelist the menu won't change

        :param menu: the Qt menu to show on middle click
        :type menu: QtWidgets.QMenu
        :param modeList: a list of menu modes (tuples) eg [("icon1", "menuName1"), ("icon2", "menuName2")]
        :type modeList: list(tuple(str))
        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        self.clickMenu[mouseButton] = menu
        self.menuActive[mouseButton] = True
        # setup the connection
        if modeList:
            self.addActionList(modeList, mouseButton=mouseButton)

    def contextMenu(self, mouseButton):
        """Draw the menu depending on mouse click

        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        menu = self.getMenu(mouseButton=mouseButton)
        # Show menu
        if menu is not None and self.menuActive[mouseButton]:
            self.setFocus()
            parentPosition = self.mapToGlobal(QtCore.QPoint(0, 0))
            # TODO: Should auto find the height of the QLineEdit
            pos = parentPosition + QtCore.QPoint(0, utils.dpiScale(self.menuVOffset))
            menu.exec_(pos)

    def getMenu(self, mouseButton=QtCore.Qt.RightButton):
        """Get menu depending on the mouse button pressed

        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        :return: The requested menu
        :rtype: QtWidgets.QMenu
        """
        return self.clickMenu[mouseButton]

    def addActionList(self, modes, mouseButton=QtCore.Qt.RightButton):
        """resets the appropriate menu with the incoming modes,
        Note: Use this method only if the menu is an ExtendedMenu from zoocore_pro

        modeList: [("icon1", "menuName1"), ("icon2", "menuName2"), ("icon3", "menuName3")]

        resets the lists and menus:

            self.menuIconList: ["icon1", "icon2", "icon3"]
            self.menuIconList: ["menuName1", "menuName2", "menuName3"]

        :param modes: a list of menu modes (tuples) eg [("icon1", "menuName1"), ("icon2", "menuName2")]
        :type modes: list(tuple(str))
        :param mouseButton: the mouse button clicked QtCore.Qt.LeftButton, QtCore.Qt.RightButton, QtCore.Qt.MiddleButton
        :type mouseButton: QtCore.Qt.ButtonClick
        """
        menu = self.getMenu(mouseButton=mouseButton)
        if menu is not None:
            menu.actionConnectList(modes)  # this only exists in ExtendedMenu which is not in zoocore


class ExtendedLineEditMenu(ExtendedLineEdit, MenuCreateClickMethods):
    leftClicked = QtCore.Signal()
    middleClicked = QtCore.Signal()
    rightClicked = QtCore.Signal()

    def __init__(self, parent=None, menuVOffset=20):
        """This class adds the capacity for a left/middle/right click menu to be added to a QLineEdit

        Inherits from zoo's ExtendedLineEdit and MenuCreateClickMethods

        Menus are not added by default they must be set in the ui code. QMenu's can be passed in via setMenu():

            zooQtWidget.setMenu(myQMenu, mouseButton=QtCore.Qt.RightButton)

        Recommended to use zoocore_pro's extendedmenu.ExtendedMenu(). Pass that in instead of a QMenu for extra
        functionality

        See the class docs for MenuCreateClickMethods() for more information

        :param parent: the parent widget
        :type parent: QWidget
        :param menuVOffset:  The vertical offset (down) menu drawn from widget top corner.  DPI is handled
        :type menuVOffset: int
        """
        super(ExtendedLineEditMenu, self).__init__(parent=parent)
        self.setupMenuClass(menuVOffset=menuVOffset)
        self.leftClicked.connect(partial(self.contextMenu, QtCore.Qt.LeftButton))
        self.middleClicked.connect(partial(self.contextMenu, QtCore.Qt.MidButton))
        self.rightClicked.connect(partial(self.contextMenu, QtCore.Qt.RightButton))

    def mousePressEvent(self, event):
        """ mouseClick emit

        Checks to see if a menu exists on the current clicked mouse button, if not, use the original Qt behaviour

        :param event: the mouse pressed event from the QLineEdit
        :type event: QEvent
        """
        for mouseButton, menu in self.clickMenu.iteritems():
            if menu and event.button() == mouseButton:  # if a menu exists and that mouse has been pressed
                if mouseButton == QtCore.Qt.LeftButton:
                    return self.leftClicked.emit()
                if mouseButton == QtCore.Qt.MidButton:
                    return self.middleClicked.emit()
                if mouseButton == QtCore.Qt.RightButton:
                    return self.rightClicked.emit()
        super(ExtendedLineEditMenu, self).mousePressEvent(event)


class ExtendedCheckboxMenu(QtWidgets.QCheckBox, MenuCreateClickMethods):
    leftClicked = QtCore.Signal()
    middleClicked = QtCore.Signal()
    rightClicked = QtCore.Signal()

    def __init__(self, label, parent=None, menuVOffset=20):
        """This class adds the capacity for a middle/right click menu to be added to the QCheckBox

        Note: This class disables the regular left click button states of a checkbox so has to handle them manual
        Inherits from QtWidgets.QCheckBox and MenuCreateClickMethods

        Menus are not added by default they must be set in the ui code. QMenu's can be passed in via setMenu():

            zooQtWidget.setMenu(myQMenu, mouseButton=QtCore.Qt.RightButton)

        If using zoocore_pro's ExtendedMenu() you can pass that in instead of a QMenu for extra functionality

        See the class docs for MenuCreateClickMethods() for more information

        :param parent: the parent widget
        :type parent: QWidget
        :param menuVOffset:  The vertical offset (down) menu drawn from widget top corner.  DPI is handled
        :type menuVOffset: int
        """
        super(ExtendedCheckboxMenu, self).__init__(label, parent=parent)
        self.setupMenuClass(menuVOffset=menuVOffset)

        self.leftClicked.connect(partial(self.contextMenu, QtCore.Qt.LeftButton))
        self.middleClicked.connect(partial(self.contextMenu, QtCore.Qt.MidButton))
        self.rightClicked.connect(partial(self.contextMenu, QtCore.Qt.RightButton))
        # TODO: the setDown should turn off as soon as the mouse moves off the widget, like a hover state, looks tricky

    def mousePressEvent(self, event):
        """ mouseClick emit

        Checks to see if a menu exists on the current clicked mouse button, if not, use the original Qt behaviour

        :param event: the mouse pressed event from the QLineEdit
        :type event: QEvent
        """
        for mouseButton, menu in self.clickMenu.iteritems():
            if menu and event.button() == mouseButton:  # if a menu exists and that mouse has been pressed
                if mouseButton == QtCore.Qt.LeftButton:
                    return self.leftClicked.emit()
                if mouseButton == QtCore.Qt.MidButton:
                    return self.middleClicked.emit()
                if mouseButton == QtCore.Qt.RightButton:
                    return self.rightClicked.emit()
        super(ExtendedCheckboxMenu, self).mousePressEvent(event)

    def setCheckedQuiet(self, value):
        """Sets the checkbox in quiet box without emitting a signal

        :param value: True if checked, False if not checked
        :type value: bool
        """
        self.blockSignals(True)
        self.setChecked(value)
        self.blockSignals(False)


class ExtendedLabelMenu(QtWidgets.QLabel, MenuCreateClickMethods):
    leftClicked = QtCore.Signal()
    middleClicked = QtCore.Signal()
    rightClicked = QtCore.Signal()

    def __init__(self, name, parent=None, menuVOffset=20):
        """This class adds the capacity for a left/middle/right click menu to be added to a QLabel

        Inherits from zoo's QtWidgets.QLabel and MenuCreateClickMethods

        Menus are not added by default they must be set in the ui code. QMenu's can be passed in via setMenu():

            zooQtWidget.setMenu(myQMenu, mouseButton=QtCore.Qt.RightButton)

        Recommended to use zoocore_pro's extendedmenu.ExtendedMenu(). Pass that in instead of a QMenu for extra
        functionality

        See the class docs for MenuCreateClickMethods() for more information

        :param parent: the parent widget
        :type parent: QWidget
        :param menuVOffset:  The vertical offset (down) menu drawn from widget top corner.  DPI is handled
        :type menuVOffset: int
        """
        super(ExtendedLabelMenu, self).__init__(name, parent=parent)
        self.setupMenuClass(menuVOffset=menuVOffset)
        self.leftClicked.connect(partial(self.contextMenu, QtCore.Qt.LeftButton))
        self.middleClicked.connect(partial(self.contextMenu, QtCore.Qt.MidButton))
        self.rightClicked.connect(partial(self.contextMenu, QtCore.Qt.RightButton))

    def mousePressEvent(self, event):
        """ mouseClick emit

        Checks to see if a menu exists on the current clicked mouse button, if not, use the original Qt behaviour

        :param event: the mouse pressed event from the QLineEdit
        :type event: QEvent
        """
        for mouseButton, menu in self.clickMenu.iteritems():
            if menu and event.button() == mouseButton:  # if a menu exists and that mouse has been pressed
                if mouseButton == QtCore.Qt.LeftButton:
                    return self.leftClicked.emit()
                if mouseButton == QtCore.Qt.MidButton:
                    return self.middleClicked.emit()
                if mouseButton == QtCore.Qt.RightButton:
                    return self.rightClicked.emit()
        super(ExtendedLabelMenu, self).mousePressEvent(event)
