from zoo.libs import iconlib
from zoo.libs.pyqt.qt import QtWidgets, QtCore


class ListViewPlus(QtWidgets.QFrame):
    selectionChanged = QtCore.Signal()
    contextMenuRequestedSignal = QtCore.Signal(object)
    refreshRequested = QtCore.Signal()

    def __init__(self, searchable=False, parent=None):
        super(ListViewPlus, self).__init__(parent)
        self.model = None

        self._setupLayouts()
        self.connections()
        self.setSearchable(searchable)

    def expandAll(self):
        self.listview.expandAll()

    def setSearchable(self, value):
        self.searchFrame.setVisible(value)

    def _setupFilter(self):
        self.searchBoxLabel = QtWidgets.QLabel("Search By: ", parent=self)
        self.searchHeaderBox = QtWidgets.QComboBox(parent=self)
        self.refreshBtn = QtWidgets.QToolButton(parent=self)
        self.refreshBtn.setIcon(iconlib.icon("reload"))
        self.searchFrame = QtWidgets.QFrame(parent=self)
        self.searchFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.searchFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.searchLayout = QtWidgets.QHBoxLayout(self)
        self.searchLayout.setContentsMargins(2, 2, 2, 2)
        self.searchClearBtn = QtWidgets.QPushButton("Clear", parent=self)
        self.searchLabel = QtWidgets.QLabel("Search", parent=self)
        self.searchEdit = QtWidgets.QLineEdit(self)
        self.searchFrame.setLayout(self.searchLayout)
        self.searchLayout.addWidget(self.refreshBtn)
        self.searchLayout.addWidget(self.searchBoxLabel)
        self.searchLayout.addWidget(self.searchHeaderBox)
        self.searchLayout.addWidget(self.searchLabel)
        self.searchLayout.addWidget(self.searchEdit)
        self.searchLayout.addWidget(self.searchClearBtn)
        self.mainLayout.addWidget(self.searchFrame)

    def _setupLayouts(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.mainLayout.setSpacing(1)
        self.listview = QtWidgets.QListView(parent=self)
        self.listview.setSelectionMode(self.listview.ExtendedSelection)
        self.listview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listview.customContextMenuRequested.connect(self.onContextMenuRequested)
        self._setupFilter()

        self.mainLayout.addWidget(self.listview)

        self.proxySearch = QtCore.QSortFilterProxyModel(parent=self)
        self.proxySearch.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.listview.setModel(self.proxySearch)
        # self.listview.setSortingEnabled(True)
        self.selectionModel = self.listview.selectionModel()

    def selectedItems(self):
        indices = self.selectionModel.selectedRows()
        model = self.model
        return [model.itemFromIndex(i) for i in indices]

    def selectedQIndices(self):
        return self.selectionModel.selectedRows()

    def connections(self):
        self.searchClearBtn.clicked.connect(self.searchEdit.clear)
        self.searchHeaderBox.currentIndexChanged.connect(self.onSearchBoxChanged)
        self.searchEdit.textChanged.connect(self.onSearchBoxChanged)
        self.refreshBtn.clicked.connect(self.refresh)

    def setModel(self, model):
        self.proxySearch.setSourceModel(model)
        self.model = model
        self.listview.setModel(self.proxySearch)
        self.searchEdit.textChanged.connect(self.proxySearch.setFilterRegExp)

    def onSearchBoxChanged(self):
        index = self.searchHeaderBox.currentIndex()
        self.proxySearch.setFilterKeyColumn(index)
        self.proxySearch.setFilterRegExp(self.searchEdit.text())

    def refresh(self):
        self.refreshRequested.emit()
        currentIndex = self.searchHeaderBox.currentIndex()
        self.searchHeaderBox.clear()
        for index in xrange(self.model.columnCount(QtCore.QModelIndex())):
            self.listview.resizeColumnToContents(index)
            newWidth = self.listview.columnWidth(index) + 10
            self.listview.setColumnWidth(index, newWidth)
            header = self.model.root.headerText(index)
            self.searchHeaderBox.addItem(header)
        self.searchHeaderBox.setCurrentIndex(currentIndex)

    def onContextMenuRequested(self, position):
        menu = QtWidgets.QMenu(parent=self)
        self.contextMenuRequestedSignal.emit(menu)
        menu.exec_(self.listview.viewport().mapToGlobal(position))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    view = listviewPlus()
    view.show()
    sys.exit(app.exec_())
