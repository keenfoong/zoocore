from zoo.libs.pyqt.qt import QtWidgets, QtCore


class TreeViewPlus(QtWidgets.QFrame):
    selectionChanged = QtCore.Signal()
    contextMenuRequested = QtCore.Signal(object, list)
    refreshRequested = QtCore.Signal()

    def __init__(self, searchable=False, parent=None, expand=True):
        super(TreeViewPlus, self).__init__(parent)

        self._setupLayouts()
        self.model = None
        self.connections()
        self.setSearchable(True)
        if expand:
            self.treeView.expandAll()

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

    def onSearchBoxChanged(self):
        self.proxySearch.setFilterKeyColumn(self.searchHeaderBox.currentIndex())

    def refresh(self):
        self.refreshRequested.emit()
        self.searchHeaderBox.clear()
        for index in xrange(self.model.columnCount(QtCore.QModelIndex())):
            self.treeView.resizeColumnToContents(index)
            newWidth = self.treeView.columnWidth(index) + 10
            self.treeView.setColumnWidth(index, newWidth)
            try:
                header = self.model.root.headerText(index)
                self.searchHeaderBox.addItem(header)
            except AttributeError:
                continue

    def contextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        self.contextMenuRequested.emit(menu, self.selectedItems())
        menu.exec_(self.treeView.viewport().mapToGlobal(position))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    view = TreeViewPlus()
    view.show()
    sys.exit(app.exec_())
