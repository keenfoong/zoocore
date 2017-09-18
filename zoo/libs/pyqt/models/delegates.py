from qt import QtWidgets, QtCore
from zoo.libs.pyqt.extended import combobox


class NumericDoubleDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        super(NumericDoubleDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()
        column = index.column()
        dataSource = model.rowDataSource
        if column == 0:
            dataSource = model.rowDataSource
            kwargs = {"index": index.row()}
        else:
            kwargs = {"rowDataSource": dataSource,
                      "index": index.row()}
            dataSource = model.columnDataSource(column)
        widget = QtWidgets.QDoubleSpinBox(parent=parent)
        widget.setMinimum(dataSource.min(**kwargs))
        widget.setMaximum(dataSource.max(**kwargs))
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
        column = index.column()
        dataSource = model.rowDataSource
        if column == 0:
            dataSource = model.rowDataSource
            kwargs = {"index": index.row()}
        else:
            kwargs = {"rowDataSource": dataSource,
                      "index": index.row()}
            dataSource = model.columnDataSource(column)
        widget = QtWidgets.QDoubleSpinBox(parent=parent)
        widget.setMinimum(dataSource.minimum(**kwargs))
        widget.setMaximum(dataSource.maximum(**kwargs))
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
        column = index.column()
        dataSource = model.rowDataSource
        if column == 0:
            dataSource = model.rowDataSource
            kwargs = {"index": index.row()}
        else:
            kwargs = {"rowDataSource": dataSource,
                      "index": index.row()}
            dataSource = model.columnDataSource(column)
        combo = combobox.ExtendedComboBox(dataSource.enums(**kwargs), parent)
        return combo

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        editor.setCurrentText(index.model().data(index, QtCore.Qt.DisplayRole))
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentIndex(), role=QtCore.Qt.EditRole)



class ButtonDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        super(ButtonDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()
        column = index.column()
        dataSource = model.rowDataSource
        if column == 0:
            dataSource = model.rowDataSource
            kwargs = {"index": index.row()}
        else:
            kwargs = {"rowDataSource": dataSource,
                      "index": index.row()}
            dataSource = model.columnDataSource(column)
        widget = QtWidgets.QPushButton(dataSource.text(**kwargs), parent=parent)
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
        column = index.column()
        dataSource = model.rowDataSource
        if column == 0:
            dataSource = model.rowDataSource
            kwargs = {"index": index.row()}
        else:
            kwargs = {"rowDataSource": dataSource,
                      "index": index.row()}
            dataSource = model.columnDataSource(column)
        widget = QtWidgets.QCheckBox(parent=parent)
        widget.clicked.connect(self.onClicked)
        widget.setChecked(dataSource.data(**kwargs))
        return widget

    def onClicked(self):
        self.commitData.emit(self.sender())

    def setEditorData(self, widget, index):
        widget.setChecked(index.model().data(index, QtCore.Qt.CheckStateRole))

    def setModelData(self, widget, model, index):
        model.setData(index, widget.isChecked(), QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
