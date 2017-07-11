from collections import OrderedDict

from zoo.libs.pyqt.qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.extended import combobox


class StringEdit(QtWidgets.QWidget):
    textChanged = QtCore.Signal(str)
    buttonClicked = QtCore.Signal()

    def __init__(self, label, placeholder, buttonText=None, parent=None):
        super(StringEdit, self).__init__(parent=parent)
        self.edit = QtWidgets.QLineEdit(parent=self)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(QtWidgets.QLabel(label, parent=self))
        self.edit.setPlaceholderText(placeholder)

        self.layout.addWidget(self.edit)
        if buttonText:
            self.btn = QtWidgets.QPushButton(buttonText, parent=self)
            self.layout.addWidget(self.btn)
        self.setLayout(self.layout)
        self.connections()

    def connections(self):
        self.edit.textChanged.connect(self._onTextChanged)

    def _onTextChanged(self):
        self.textChanged.emit(str(self.edit.text()))

    def setText(self, value):
        self.edit.setText(value)


class ComboBox(QtWidgets.QWidget):
    itemChanged = QtCore.Signal(int, str)

    def __init__(self, label, items, parent=None):
        super(ComboBox, self).__init__(parent=parent)
        layout = QtWidgets.QHBoxLayout(self)

        self.box = combobox.ExtendedComboBox(items, parent)
        self.label = QtWidgets.QLabel(label, parent=self)

        layout.addWidget(self.label)
        layout.addWidget(self.box)
        self.setLayout(layout)

        self.box.currentIndexChanged.emit(self.onItemChanged)

    def onItemChanged(self):
        self.itemChanged.emit(int(self.box.currentIndex()), str(self.box.currentText()))


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
    rotOrders = ("XYZ", "YZX", "ZXY", "XZY", "XYZ", "ZXY")
    axis = ("X", "Y", "Z")

    def __init__(self, parent=None):
        super(Transformation, self).__init__(parent=parent)
        self.group = QtWidgets.QGroupBox(parent=self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.group.setLayout(self.layout)
        translationVec = Vector("Translation", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        rotationVec = Vector("Rotation", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        scaleVec = Vector("Scale", [0.0, 0.0, 0.0], -99999, 99999, Transformation.axis, parent=self)
        rotationOrderBox = ComboBox("RotationOrder", Transformation.rotOrders, parent=self)
        self.layout.addWidget(translationVec)
        self.layout.addWidget(rotationVec)
        self.layout.addWidget(rotationVec)
        self.layout.addWidget(scaleVec)
        self.layout.addWidget(rotationOrderBox)
        self.setLayout(self.layout)
