from qt import QtCore, QtWidgets

from zoo.libs import iconlib
from zoo.libs.pyqt import utils
from zoo.libs.pyqt.extended import combobox, searchwidget


class ViewSearchWidget(QtWidgets.QWidget):
    """Specialized widget for column row views eg. table view,

    contains::
    
        column Visibility combobox,
        column Filter combobox,
        Search Widget

    Signals::

        ColumnVisibilityIndexChanged
        ColumnFilterIndexChanged
        SearchTextedChanged
        SearchTextedCleared

    """
    columnVisibilityIndexChanged = QtCore.Signal(int, str)
    columnFilterIndexChanged = QtCore.Signal(int, str)
    searchTextedChanged = QtCore.Signal(str)
    searchTextedCleared = QtCore.Signal()

    def __init__(self, showColumnVisBox=True, showHeaderBox=True, parent=None):
        super(ViewSearchWidget, self).__init__(parent=parent)
        searchIcon = iconlib.iconColorized("magnifier", size=utils.dpiScale(14), color=(128, 128, 128))
        closeIcon = iconlib.iconColorized("close", size=utils.dpiScale(14), color=(128, 128, 128))

        self.searchFrame = QtWidgets.QFrame(parent=self)
        self.searchFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.searchFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.searchLayout = QtWidgets.QHBoxLayout(self)
        self.searchLayout.setContentsMargins(0, 0, 0, 0)

        self.searchWidget = searchwidget.SearchLineEdit(searchIcon, closeIcon, parent=self)
        self.searchWidget.textCleared.connect(self.searchTextedCleared.emit)
        self.searchWidget.textChanged.connect(self.searchTextedChanged.emit)

        self.searchFrame.setLayout(self.searchLayout)

        self.columnVisibilityBox = combobox.ExtendedComboBox(parent=self)
        self.columnVisibilityBox.setMinimumWidth(100)
        self.columnVisibilityBox.checkStateChanged.connect(self.onVisibilityChanged)
        self.searchLayout.addWidget(self.columnVisibilityBox)

        self.searchHeaderBox = combobox.ExtendedComboBox(parent=self)
        self.searchHeaderBox.setMinimumWidth(100)
        self.searchHeaderBox.currentIndexChanged.connect(self.onFilterChanged)
        self.searchLayout.addWidget(self.searchHeaderBox)
        self.searchLayout.addWidget(self.searchWidget)
        if not showColumnVisBox:
            self.columnVisibilityBox.hide()
        if not showHeaderBox:
            self.searchHeaderBox.hide()

    def setVisibilityItems(self, items):
        self.columnVisibilityBox.clear()
        for i in items:
            self.columnVisibilityBox.addItem(i, isCheckable=True)

    def setHeaderItems(self, items):
        self.searchHeaderBox.clear()
        for i in items:
            self.searchHeaderBox.addItem(i, isCheckable=False)

    def onVisibilityChanged(self, index):
        self.columnVisibilityIndexChanged.emit(int(index), self.columnVisibilityBox.currentText())

    def onFilterChanged(self, index):
        self.columnFilterIndexChanged.emit(int(index), self.searchHeaderBox.currentText())
