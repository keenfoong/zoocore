from zoo.libs.pyqt.qt import QtWidgets, QtGui
from zoo.libs.pyqt.extended import combobox


class ComboDelegate(QtGui.QItemDelegate):
    def __init__(self, parent, options):
        QtGui.QItemDelegate.__init__(self, parent)
        self.options = options

    def createEditor(self, parent, option, index):
        combo = combobox.ExtendedComboBox(parent)
        combo.addItems(self.options)
        combo.currentIndexChanged.connect(self.currentIndexChanged)
        return combo

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        editor.setCurrentIndex(editor.currentIndex())
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.itemText(editor.currentIndex()))

    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


class ButtonDelegate(QtGui.QItemDelegate):

    def __init__(self, parent):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        combo = QtGui.QPushButton(str(index.data()), parent)
        combo.clicked.connect(self.currentIndexChanged)
        return combo

    def setEditorData(self, editor, index):
        pass
    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())

    def currentIndexChanged(self):
        self.commitData.emit(self.sender())