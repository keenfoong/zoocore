from zoo.libs import iconlib
from zoo.libs.pyqt.qt import QtWidgets, QtCore


class TreeViewPlus(QtWidgets.QFrame):
    selectionChanged = QtCore.Signal()
    contextMenuRequestedSignal = QtCore.Signal(object)
    refreshRequested = QtCore.Signal()

    def __init__(self, searchable=False, parent=None):
        super(TreeViewPlus, self).__init__(parent)
        self.model = None

        self._setupLayouts()
        self.connections()
        self.setSearchable(searchable)

    def expandAll(self):
        self.treeView.expandAll()

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
        self.treeView = QtWidgets.QTreeView(parent=self)
        self.treeView.setSelectionMode(self.treeView.ExtendedSelection)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.onContextMenuRequested)
        self._setupFilter()

        self.mainLayout.addWidget(self.treeView)

        self.proxySearch = QtCore.QSortFilterProxyModel(parent=self)
        self.proxySearch.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.treeView.setModel(self.proxySearch)
        self.treeView.setSortingEnabled(True)
        self.selectionModel = self.treeView.selectionModel()

    def selectedItems(self):
        indices = self.selectionModel.selectedRows()
        model = self.model
        return [model.itemFromIndex(i) for i in indices]

    def selectedQIndices(self):
        return self.selectionModel.selectedRows()
        
    def onExpanded(self, index):
        column = index.column()
        self.treeView.resizeColumnToContents(column)
        newWidth = self.treeView.columnWidth(column) + 10
        self.treeView.setColumnWidth(column, newWidth)

    def connections(self):
        self.treeView.expanded.connect(self.onExpanded)
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
        self.treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.model = model
        self.treeView.setModel(self.proxySearch)
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
            self.treeView.resizeColumnToContents(index)
            newWidth = self.treeView.columnWidth(index) + 10
            self.treeView.setColumnWidth(index, newWidth)
            header = self.model.root.headerText(index)
            self.searchHeaderBox.addItem(header)
        self.searchHeaderBox.setCurrentIndex(currentIndex)

    def onContextMenuRequested(self, position):
        menu = QtWidgets.QMenu(parent=self)
        self.contextMenuRequestedSignal.emit(menu)
        menu.exec_(self.treeView.viewport().mapToGlobal(position))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    view = TreeViewPlus()
    view.show()
    sys.exit(app.exec_())
