from qt import QtCore, QtGui, QtWidgets
from zoo.libs.pyqt.extended import combobox
from zoo.libs.pyqt.extended import searchwidget
from zoo.libs import iconlib


class ViewSearchWidget(QtWidgets.QWidget):
    """Specialize widget for column row views eg. table view,
    contains:
        column Visibility combobox,
        column Filter combobox,
        Search Widget
    Signals
        ColumnVisibilityIndexChanged
        ColumnFilterIndexChanged
        SearchTextedChanged
        SearchTextedCleared
    """
    columnVisibilityIndexChanged = QtCore.Signal(int, str)
    columnFilterIndexChanged = QtCore.Signal(int, str)
    searchTextedChanged = QtCore.Signal(str)
    searchTextedCleared = QtCore.Signal()

    def __init__(self, showColumnVisBox=True, parent=None):
        super(ViewSearchWidget, self).__init__(parent=parent)
        searchIcon = iconlib.icon("magnifier", 16)
        closeIcon = iconlib.icon("close", 16)

        self.searchFrame = QtWidgets.QFrame(parent=self)
        self.searchFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.searchFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.searchLayout = QtWidgets.QHBoxLayout(self)
        self.searchLayout.setContentsMargins(2, 2, 2, 2)

        self.searchBoxLabel = QtWidgets.QLabel("Search By: ", parent=self)
        self.searchHeaderBox = combobox.ExtendedComboBox(parent=self)
        self.searchHeaderBox.setMinimumWidth(100)
        self.searchWidget = searchwidget.SearchLineEdit(searchIcon, closeIcon, parent=self)

        self.searchHeaderBox.currentIndexChanged.connect(self.onFilterChanged)
        self.searchWidget.textCleared.connect(self.searchTextedCleared.emit)
        self.searchWidget.textChanged.connect(self.searchTextedChanged.emit)

        self.searchFrame.setLayout(self.searchLayout)

        self.columnVisibilityBox = None
        if showColumnVisBox:
            self.columnVisibilityBox = combobox.ExtendedComboBox(parent=self)
            self.columnVisibilityBox.setMinimumWidth(100)
            self.columnVisibilityBox.checkStateChanged.connect(self.onVisibilityChanged)
            self.searchLayout.addWidget(self.columnVisibilityBox)

        self.searchLayout.addWidget(self.searchBoxLabel)
        self.searchLayout.addWidget(self.searchHeaderBox)
        self.searchLayout.addWidget(self.searchWidget)

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
