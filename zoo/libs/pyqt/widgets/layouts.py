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
            self.btn = QtWidgets.QPushButton(buttonText, parent=self)
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
        self.valueChanged.emit(tuple([tuple([float(t.value()) for t in c]) for c in self._widgets.values()]))

    def widget(self, column):
        return self._widgets.get(column)


class Transformation(QtWidgets.QWidget):
    # @todo setup signals
    rotOrders = ("XYZ", "YZX", "ZXY", "XZY", "XYZ", "ZYX")
    axis = ("X", "Y", "Z")

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
    def __init__(self, radioList=None, default=0, parent=None):
        super(HRadioButtonGroup, self).__init__(parent=parent)
        if radioList is None:
            radioList = []

        self.radioButtons = []

        hRadioLayout = QtWidgets.QHBoxLayout()

        for radioName in radioList:
            newRadio = QtWidgets.QRadioButton(radioName,self)
            hRadioLayout.addWidget(newRadio)
            self.radioButtons.append(newRadio)

        if default is not None and default < len(self.radioButtons):
            self.radioButtons[default].setChecked(True)

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


class StackWidget(QtWidgets.QWidget):
    _expandIcon = iconlib.icon("roundedsquare")
    _collapseIcon = iconlib.icon("minus")

    def __init__(self,parent):
        super(StackWidget, self).__init__()

        self.stackTableWgt = StackTableWidget(self)
        self.stackSearchEdit = QtWidgets.QLineEdit()
        self.collapseBtn = QtWidgets.QPushButton()
        self.expandBtn = QtWidgets.QPushButton()
        self.initUi()

        self.connections()

    def initUi(self):

        compStackToolbar = QtWidgets.QHBoxLayout()
        compStackToolbar.addWidget(self.stackSearchEdit)

        self.expandBtn.setIcon(self._expandIcon)
        self.expandBtn.setIconSize(QtCore.QSize(12, 12))

        self.collapseBtn.setIcon(self._collapseIcon)
        self.collapseBtn.setIconSize(QtCore.QSize(10, 10))

        size = QtCore.QSize(self.collapseBtn.sizeHint().width(), 20) # Temporary size till we get icons here
        self.collapseBtn.setFixedSize(size)
        self.expandBtn.setFixedSize(size)

        compStackToolbar.addWidget(self.collapseBtn)
        compStackToolbar.addWidget(self.expandBtn)
        compStackToolbar.setStretchFactor(self.stackSearchEdit, 1)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(QtWidgets.QLabel("Installed Components"))
        mainLayout.addLayout(compStackToolbar)
        mainLayout.addWidget(self.stackTableWgt)

        self.setLayout(mainLayout)

    def connections(self):
        self.stackSearchEdit.textChanged.connect(self.onStackSearchChanged)

        self.collapseBtn.clicked.connect(self.collapseClicked)
        self.expandBtn.clicked.connect(self.expandClicked)

    def collapseClicked(self):
        self.stackTableWgt.collapseAll()

    def expandClicked(self):
        self.stackTableWgt.expandAll()

    def onStackSearchChanged(self):
        text = self.stackTableWgt.text().lower()
        self.stackTableWgt.filter(text)
        self.stackTableWgt.updateSize()

    def clearStack(self):
        self.stackTableWgt.clearStack()


class StackTableWidget(QtWidgets.QTableWidget):
    DEFAULT_MAYA_COLOUR = (68, 68, 68)
    def __init__(self, parent=None):
        super(StackTableWidget, self).__init__(parent)

        self.stackItems = []
        self.initUi()
        self.setShowGrid(False)
        self.cellPadding = 5

        style = """
            QTableView {{
            background-color: rgb{0};
            border-size: 0px;
            }}

            QTableView:item {{
            padding:{1}px;
            border-size: 0px;
            }}
            """.format(str(self.DEFAULT_MAYA_COLOUR), self.cellPadding)

        self.setStyleSheet(style)

    def initUi(self):
        self.setRowCount(0)
        self.setColumnCount(1)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        self.horizontalHeader().setStretchLastSection(True)

        self.setContentsMargins(2, 2, 2, 2)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def shiftComponentWidget(self, wgt, dir):
        # Update componentList
        self.shiftComponentStack(wgt, dir)

        row = self.getRow(wgt)

        if row == 0 and dir == -1 or \
                                row == self.rowCount() - 1 and dir == 1:
            return

        # newRow = row + dir
        # Have to do this in a funky way because removeRow deletes the object
        # and swapping cells gives weird results
        if dir > 0:  # Even then this is ugly lol, need to fix
            newRow = row + dir + 1
            remRow = row
        else:
            newRow = row + dir
            remRow = row + 1

        self.insertRow(newRow)
        self.setCellWidget(newRow, 0, wgt)
        self.removeRow(remRow)
        self.updateSize(wgt)

        # Update the back end component
        self.core.shiftComponent(wgt.component, dir)

    def shiftComponentStack(self, wgt, dir):
        i = self.stackItems.index(wgt)
        self.stackItems.remove(wgt)
        self.stackItems.insert(i + dir, wgt)

    def collapseAll(self):
        for c in self.stackItems:
            c.collapse()

    def expandAll(self):
        for c in self.stackItems:
            c.expand()

    def deleteComponent(self, wgt):
        row = self.getRow(wgt)
        self.removeRow(row)
        self.stackItems.remove(wgt)
        self.core.deleteComponent(wgt.component)
        wgt.deleteLater()
        self.updateComponentWidgets()

    def addStackItem(self, item):
        self.componentStack.append(item)
        self.addRow(item)
        self.updateSize()
        self.updateComponentWidgets()

    def addRow(self, componentWgt):
        rowPos = self.rowCount()
        self.setRowCount(rowPos + 1)
        self.setItem(rowPos, 0, QtWidgets.QTableWidgetItem())
        self.setCellWidget(rowPos, 0, componentWgt)
        self.updateSize(componentWgt)
        self.setRowHeight(rowPos, componentWgt.sizeHint().height() + 100)

    def getRow(self, componentWgt):
        for i in range(self.rowCount()):
            if componentWgt == self.cellWidget(i, 0):
                return i

    def filter(self, text):
        for i in range(self.rowCount()):
            found = not (text in self.cellWidget(i, 0).component.name().lower())
            self.setRowHidden(i, found)

    def updateComponentWidgets(self):
        for c in self.stackItems:
            c.updateComponents()

    def getStackItems(self):
        # stackItems = [self.stackLayout.itemAt(i) for i in range(self.stackLayout.count())]
        return self.stackItems

    def updateSize(self, forceComponent=None):

        if forceComponent is not None:
            componentWgt = forceComponent
        else:
            componentWgt = self.sender()

            if componentWgt is None:
                return

        newHeight = componentWgt.sizeHint().height() + self.cellPadding * 2
        self.setRowHeight(self.getRow(componentWgt), newHeight)

    def clearStack(self):
        self.stackItems = []
        self.clear()
        self.setRowCount(0)

    def sceneRefresh(self):
        self.clearStack()

    def applyRig(self, rig):
        self.sceneRefresh()

        if rig is not None:
            for c in rig.components():
                self.addComponent(c)


class ComponentStackItem(CollapsableFrameLayout):
    _downIcon = iconlib.icon("arrowSingleDown")
    _upIcon = iconlib.icon("arrowSingleUp")
    _deleteIcon = iconlib.icon("xMark")
    _componentIcon = iconlib.icon("fkcomponentsimple")
    #_componentIcon = iconlib.iconColorized("fkcomponentsimple", color=const.UI_THEMECOLOUR)

    def __init__(self, component, collapsed=False, collapsable=True, parent=None):
        self.stackWidget = parent
        self.component = component
        title = self.component.name()
        # Init
        self.componentIcon = QtWidgets.QToolButton()
        self.shiftDownBtn = QtWidgets.QToolButton()
        self.shiftUpBtn = QtWidgets.QToolButton()
        self.deleteBtn = QtWidgets.QToolButton()
        self.componentNameWgt = QtWidgets.QLineEdit(title)
        self.mainLayout = QtWidgets.QGridLayout()

        super(ComponentStackItem, self).__init__(title=title, collapsed=collapsed, collapsable=collapsable,
                                                 parent=parent)

        # self.initUi()

    def initUi(self):
        super(ComponentStackItem, self).initUi()
        sideNames = sorted(self.getSideNames())
        self.parentComboBox = combobox.ExtendedComboBox([""], parent=self)
        self.sideComboBox = combobox.ExtendedComboBox([""] + sideNames, parent=self)

        self.componentIcon.setIcon(self._componentIcon)
        self.shiftDownBtn.setIcon(self._downIcon)
        self.shiftUpBtn.setIcon(self._upIcon)
        self.deleteBtn.setIcon(self._deleteIcon)

        self.deleteBtn.setIconSize(QtCore.QSize(12, 12))
        self.shiftUpBtn.setIconSize(QtCore.QSize(12, 12))
        self.shiftDownBtn.setIconSize(QtCore.QSize(12, 12))
        # self.componentIcon.setIconSize(QtCore.QSize(24, 24))

        self.horizontalLayout.insertWidget(1, self.componentIcon)
        self.horizontalLayout.addWidget(self.shiftUpBtn)
        self.horizontalLayout.addWidget(self.shiftDownBtn)
        self.horizontalLayout.addWidget(self.deleteBtn)

        # Possibly should tweak layouts.CollapsableFrameLayout (or create a new class) instead of adding then deleting
        i = self.horizontalLayout.indexOf(self.titleLabel)
        self.horizontalLayout.takeAt(i)
        self.titleLabel.deleteLater()
        self.horizontalLayout.insertWidget(2, self.componentNameWgt)
        self.horizontalLayout.setStretchFactor(self.componentNameWgt, 4)

        # Main Layout
        self.mainLayout.setSpacing(0)

        row = 0
        self.mainLayout.addWidget(QtWidgets.QLabel("Parent:"), row, 0, 1, 1)
        self.mainLayout.addWidget(self.parentComboBox, row, 1, 1, 1)
        row += 1
        self.mainLayout.addWidget(QtWidgets.QLabel("Side:"), row, 0, 1, 1)

        self.mainLayout.addWidget(self.sideComboBox, row, 1, 1, 1)
        self.mainLayout.setColumnStretch(0, 1)
        self.mainLayout.setColumnStretch(1, 1)
        row += 1

        widget = QtWidgets.QWidget()
        widget.setLayout(self.mainLayout)

        self.hiderLayout.addWidget(widget)

        self.stackConnections()
        self.updateUi()

    def shiftUp(self):
        self.stackWidget.shiftComponentWidget(self, -1)

    def shiftDown(self):
        self.stackWidget.shiftComponentWidget(self, 1)

    def expand(self):
        self.onExpand()

    def collapse(self):
        self.onCollapsed()

    def updateUi(self):
        """
        Updates Ui based on self.component
        :return:
        """

        # self.sideComboBox.setCurrentIndex(2) # Magical

    def setComboToText(self, combobox, text):
        index = combobox.findText(text, QtCore.Qt.MatchFixedString)
        combobox.setCurrentIndex(index)

    def deleteEvent(self):
        # self.delFunc(self)
        self.stackWidget.deleteComponent(self)

    def stackConnections(self):
        self.openRequested.connect(self.stackWidget.updateSize)
        self.closeRequested.connect(self.stackWidget.updateSize)

        self.shiftUpBtn.clicked.connect(self.shiftUp)
        self.shiftDownBtn.clicked.connect(self.shiftDown)
        self.deleteBtn.clicked.connect(self.deleteEvent)

        self.componentNameWgt.editingFinished.connect(self.renameComponent)
        self.componentNameWgt.textChanged.connect(self.componentNameValidate)

        self.parentComboBox.activated.connect(self.parentComboActivated)
        self.sideComboBox.activated.connect(self.setSide)

    def componentNameValidate(self):
        """
        Removes invalid characters and replaces spaces with underscores
        :return:
        """
        nameWgt = self.componentNameWgt
        text = self.componentNameWgt.text()
        pos = nameWgt.cursorPosition()

        text = text.replace(" ", "_")
        nameWgt.blockSignals(True)
        nameWgt.setText(text)
        nameWgt.blockSignals(False)

        # set cursor back to original position
        nameWgt.setCursorPosition(pos)

    def getSideNames(self):
        sideNames = []
        side = self.sceneModel.configuration.naming.config["tokens"]["side"]
        tokens = self.sceneModel.configuration.naming.tokenValues('side')

        for t in tokens:
            sideNames.append(side[t])

        return sideNames

    def updateSize(self):
        self.stackWidget.updateSize()

    def renameComponent(self):
        component = self.component
        component.rename(self.sender().text())

    def updateComponents(self):
        # Update parentCombobox widget
        componentList = [""] + [c.name() for c in self.core.components()]
        parentBox = self.parentComboBox
        parentText = parentBox.currentText()

        componentList.remove(self.component.name())
        parentBox.clear()
        parentBox.addItems(componentList)
        try:
            parentText = self.component.parent().name()
            print(parentText)

        except AttributeError:
            pass
        self.setComboToText(self.parentComboBox, parentText)

        # Part two
        side = self.component.side()

        # Two
        self.setComboToText(self.sideComboBox, side)


        # self.parentComboBox.setCurrentIndex(1)

    def parentComboActivated(self):

        parentText = self.parentComboBox.currentText()

        parentComponent = None
        for c in self.core.components():
            if c.name() == parentText:
                parentComponent = c
                break

        if parentComponent is None:
            componentLayer = self.core.currentRig.getOrCreateComponentLayer()
            self.component.setParent(componentLayer)
            return

        self.component.setParent(parentComponent)

    def setSide(self):
        side = self.sideComboBox.currentText()
        self.component.setSide(side)

    def setFrameColor(self, color):
        style = """
            QFrame, QToolButton
            {{
                background-color: rgb{0};
                border-radius: 3px;
                border: 1px solid rgb{0};

            }}
            QLineEdit
            {{
                background-color: rgb{1};
            }}
            """.format(str(color), str((63, 63, 63)))

        self.titleFrame.setStyleSheet(style)
