from zoo.libs import iconlib
from zoo.libs.pyqt.qt import QtWidgets, QtCore


class TableViewPlus(QtWidgets.QFrame):
    selectionChanged = QtCore.Signal()
    contextMenuRequestedSignal = QtCore.Signal(object)
    refreshRequested = QtCore.Signal()

    def __init__(self, searchable=False, parent=None):
        super(TableViewPlus, self).__init__(parent)
        self.model = None

        self._setupLayouts()
        self.connections()
        self.setSearchable(searchable)

    def expandAll(self):
        self.tableView.expandAll()

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
        self.tableView = QtWidgets.QTableView(parent=self)
        self.tableView.setSelectionMode(self.tableView.ExtendedSelection)
        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.onContextMenuRequested)
        self._setupFilter()

        self.mainLayout.addWidget(self.tableView)

        self.proxySearch = QtCore.QSortFilterProxyModel(parent=self)
        self.proxySearch.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.tableView.setModel(self.proxySearch)
        self.tableView.setSortingEnabled(True)
        self.selectionModel = self.tableView.selectionModel()

    def selectedItems(self):
        indices = self.selectionModel.selectedRows()
        model = self.model
        return [model.itemFromIndex(i) for i in indices]

    def selectedQIndices(self):
        return self.selectionModel.selectedRows()

    def connections(self):
        self.tableView.expanded.connect(self.refresh)
        self.tableView.collapsed.connect(self.refresh)
        self.searchClearBtn.clicked.connect(self.searchEdit.clear)
        self.searchHeaderBox.currentIndexChanged.connect(self.onSearchBoxChanged)
        self.searchEdit.textChanged.connect(self.onSearchBoxChanged)
        self.refreshBtn.clicked.connect(self.refresh)

    def setModel(self, model):
        self.proxySearch.setSourceModel(model)
        self.proxySearch.setDynamicSortFilter(True)
        self.proxySearch.setSortRole(QtCore.Qt.DisplayRole)
        self.proxySearch.setFilterRole(QtCore.Qt.DisplayRole)
        self.proxySearch.setFilterKeyColumn(0)
        self.proxySearch.setFilterRegExp(self.searchEdit.text())
        self.tableView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.model = model
        self.tableView.setModel(self.proxySearch)
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
            self.tableView.resizeColumnToContents(index)
            newWidth = self.tableView.columnWidth(index) + 10
            self.tableView.setColumnWidth(index, newWidth)
            header = self.model.root.headerText(index)
            self.searchHeaderBox.addItem(header)
        self.searchHeaderBox.setCurrentIndex(currentIndex)

    def onContextMenuRequested(self, position):
        menu = QtWidgets.QMenu(parent=self)
        self.contextMenuRequestedSignal.emit(menu)
        menu.exec_(self.tableView.viewport().mapToGlobal(position))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    view = TableViewPlus()
    view.show()
    sys.exit(app.exec_())
