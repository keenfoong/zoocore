from zoo.libs.pyqt.qt import QtWidgets, QtCore


class TreeViewPlus(QtWidgets.QFrame):
    selectionChanged = QtCore.Signal()
    contextMenuRequested = QtCore.Signal(object, list)
    refreshRequested = QtCore.Signal()

    def __init__(self, searchable=False, parent=None, expand=True):
        super(TreeViewPlus, self).__init__(parent)

        self._setupLayouts()
        self.model = None
        self.rowDataSource = None
        self.columnDataSources = []
        self.connections()
        self.setSearchable(True)
        if expand:
            self.treeView.expandAll()

    def registerRowDataSource(self, dataSource):
        self.rowDataSource = dataSource
        if hasattr(dataSource, "delegate"):
            delegate = dataSource.delegate(self.tableview)
            self.tableview.setItemDelegateForColumn(0, delegate)
        self._model.rowDataSource = dataSource

    def registerColumnDataSources(self, dataSources):
        if not self.rowDataSource:
            raise ValueError("Must assign rowDataSource before columns")
        self.columnDataSources = dataSources
        for i in xrange(len(dataSources)):
            source = dataSources[i]
            if hasattr(source, "delegate"):
                delegate = source.delegate(self.tableview)
                self.tableview.setItemDelegateForColumn(i + 1, delegate)

        self._model.columnDataSources = dataSources

    def expandAll(self):
        self.treeView.expandAll()

    def setSearchable(self, value):
        self.searchFrame.setVisible(value)

    def _setupFilter(self):
        self.searchBoxLabel = QtWidgets.QLabel("Search By: ", parent=self)
        self.searchHeaderBox = QtWidgets.QComboBox(parent=self)

        self.searchFrame = QtWidgets.QFrame(parent=self)
        self.searchFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.searchFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.searchLayout = QtWidgets.QHBoxLayout(self)
        self.searchLayout.setContentsMargins(2, 2, 2, 2)
        self.searchClearBtn = QtWidgets.QPushButton("Clear", parent=self)
        self.searchLabel = QtWidgets.QLabel("Search", parent=self)
        self.searchEdit = QtWidgets.QLineEdit(self)
        self.searchEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.searchFrame.setLayout(self.searchLayout)
        self.searchLayout.addWidget(self.searchBoxLabel)
        self.searchLayout.addWidget(self.searchHeaderBox)
        self.searchLayout.addWidget(self.searchLabel)
        self.searchLayout.addWidget(self.searchEdit)
        self.searchLayout.addWidget(self.searchClearBtn)
        self.mainLayout.addWidget(self.searchFrame)

    def _setupLayouts(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.treeView = QtWidgets.QTreeView(parent=self)
        self.treeView.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.treeView.setSelectionMode(self.treeView.ExtendedSelection)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.contextMenu)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setRootIsDecorated(True)
        self.treeView.setSortingEnabled(True)
        self._setupFilter()

        self.mainLayout.addWidget(self.treeView)

        self.proxySearch = QtCore.QSortFilterProxyModel(parent=self)
        self.proxySearch.setDynamicSortFilter(True)
        self.proxySearch.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.treeView.setModel(self.proxySearch)
        self.selectionModel = self.treeView.selectionModel()

    def selectedItems(self):
        indices = self.selectionModel.selectedRows()
        model = self.model
        return [model.itemFromIndex(i) for i in indices]

    def selectedQIndices(self):
        indices = self.selectionModel.selectedRows()
        return indices

    def connections(self):
        self.treeView.expanded.connect(self.refresh)
        self.treeView.collapsed.connect(self.refresh)
        self.searchClearBtn.clicked.connect(self.searchEdit.clear)
        self.searchHeaderBox.currentIndexChanged.connect(self.onSearchBoxChanged)
        self.searchEdit.textChanged.connect(self.proxySearch.setFilterRegExp)

    def setModel(self, model):
        self.model = model
        self.proxySearch.setSourceModel(model)
        if self.rowDataSource:
            self.rowDataSource.model = model
        for i in iter(self.columnDataSources):
            i.model = model
        self.treeView.setModel(self.model)
        
    def onSearchBoxChanged(self):
        self.proxySearch.setFilterKeyColumn(self.searchHeaderBox.currentIndex())

    def refresh(self):
        self.refreshRequested.emit()
        self.searchHeaderBox.clear()
        rowDataSource = self._model.rowDataSource
        columnDataSources = self._model.columnDataSources
        self.searchHeaderBox.addItem(rowDataSource.headerText(0))
        for i in xrange(len(columnDataSources)):
            self.searchHeaderBox.addItem(columnDataSources[i].headerText(i))
            self.treeView.resizeColumnToContents(index)
            newWidth = self.treeView.columnWidth(index) + 10
            self.treeView.setColumnWidth(index, newWidth)
            header = self.model.root.headerText(index)
            self.searchHeaderBox.addItem(header)

    def contextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        selection = self.selectedRows()
        if self.rowDataSource:
            self.rowDataSource.contextMenu(selection, menu)
        self.contextMenuRequested.emit(selection, menu)
        menu.exec_(self.treeview.viewport().mapToGlobal(position))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    view = TreeViewPlus()
    view.show()
    sys.exit(app.exec_())
