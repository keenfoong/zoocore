from qt import QtWidgets, QtCore
from zoo.libs.pyqt.extended import combobox
from zoo.libs.pyqt.models import constants


class NumericDoubleDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        super(NumericDoubleDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()
        widget = QtWidgets.QDoubleSpinBox(parent=parent)
        widget.setMinimum(model.data(index, constants.minValue))
        widget.setMaximum(constants.maxValue)
        return widget

    def setEditorData(self, widget, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        widget.setValue(value)

    def setModelData(self, widget, model, index):
        value = widget.value()
        model.setData(index, value, QtCore.QtEditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class NumericIntDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        super(NumericIntDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()
        widget = QtWidgets.QDoubleSpinBox(parent=parent)
        widget.setMinimum(model.data(index,constants.minValue))
        widget.setMaximum(model.data(index,constants.maxValue))
        return widget

    def setEditorData(self, widget, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        widget.setValue(value)

    def setModelData(self, widget, model, index):
        value = widget.value()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class EnumerationDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        super(EnumerationDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()
        combo = combobox.ExtendedComboBox(model.data(index, constants.enumsRole), parent)
        return combo

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        text = index.model().data(index, QtCore.Qt.DisplayRole)
        index = editor.findText(text, QtCore.Qt.MatchFixedString)
        if index >= 0:
            editor.setCurrentIndex(index)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentIndex(), role=QtCore.Qt.EditRole)



class ButtonDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        super(ButtonDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()

        widget = QtWidgets.QPushButton(model.data(QtCore.Qt.DisplayRole), parent=parent)
        widget.clicked.connect(self.onClicked)
        return widget

    def onClicked(self):
        self.commitData.emit(self.sender())

    def setEditorData(self, widget, index):
        pass

    def setModelData(self, widget, model, index):
        model.setData(index, 1, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CheckBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        super(CheckBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()
        widget = QtWidgets.QCheckBox(parent=parent)
        widget.clicked.connect(self.onClicked)
        widget.setChecked(model.data(index, QtCore.Qt.DisplayRole))
        return widget

    def onClicked(self):
        self.commitData.emit(self.sender())

    def setEditorData(self, widget, index):
        widget.setChecked(index.model().data(index, QtCore.Qt.CheckStateRole))

    def setModelData(self, widget, model, index):
        model.setData(index, widget.isChecked(), QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
