from qt import QtWidgets, QtCore
from zoo.libs import iconlib
from zoo.libs.pyqt.extended import viewfilterwidget


class TreeViewPlus(QtWidgets.QFrame):
    selectionChanged = QtCore.Signal(list, list)
    contextMenuRequested = QtCore.Signal(object, list)
    refreshRequested = QtCore.Signal()

    def __init__(self, searchable=False, parent=None, expand=True):
        super(TreeViewPlus, self).__init__(parent)

        self._setupLayouts()
        self.model = None
        self.rowDataSource = None
        self.columnDataSources = []
        self.connections()
        self.setSearchable(searchable)
        if expand:
            self.treeView.expandAll()

    def registerRowDataSource(self, dataSource):
        self.rowDataSource = dataSource
        if hasattr(dataSource, "delegate"):
            delegate = dataSource.delegate(self.tableview)
            self.tableview.setItemDelegateForColumn(0, delegate)
        self.model.rowDataSource = dataSource

    def registerColumnDataSources(self, dataSources):
        if not self.rowDataSource:
            raise ValueError("Must assign rowDataSource before columns")
        self.columnDataSources = dataSources
        for i in xrange(len(dataSources)):
            source = dataSources[i]
            if hasattr(source, "delegate"):
                delegate = source.delegate(self.tableview)
                self.tableview.setItemDelegateForColumn(i + 1, delegate)

        self.model.columnDataSources = dataSources

    def expandAll(self):
        self.treeView.expandAll()

    def setSearchable(self, value):
        self.searchWidget.setVisible(value)

    def _setupFilter(self):
        self.reloadBtn = QtWidgets.QToolButton(parent=self)
        self.reloadBtn.setIcon(iconlib.icon("reload"))
        self.searchLayout = QtWidgets.QHBoxLayout(self)
        self.searchLayout.setContentsMargins(2, 2, 2, 2)
        self.searchLayout.addWidget(self.reloadBtn)
        # setup the column search widget
        self.searchWidget = viewfilterwidget.ViewSearchWidget(showColumnVisBox=False, parent=self)
        self.searchLayout.addWidget(self.searchWidget)
        self.mainLayout.addLayout(self.searchLayout)

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

    def _headerMenu(self, pos):
        globalPos = self.mapToGlobal(pos)
        menu = QtWidgets.QMenu(parent=self)
        headers = self.headerItems()
        for i in range(len(headers)):
            item = QtWidgets.QAction(headers[i], menu, checkable=True)
            menu.addAction(item)
            item.setChecked(not self.treeView.header().isSectionHidden(i))
            item.setData({"index": i})
        selectedItem = menu.exec_(globalPos)
        self.toggleColumn(selectedItem.data()["index"],
                          QtCore.Qt.Checked if selectedItem.isChecked() else QtCore.Qt.Unchecked)

    def headerItems(self):
        headerItems = []
        for index in xrange(self.model.columnCount(QtCore.QModelIndex())):
            headerItems.append(self.model.root.headerText(index))
        return headerItems

    def selectedItems(self):
        indices = self.selectedQIndices()
        model = self.model
        return [model.itemFromIndex(i) for i in indices]

    def selectedQIndices(self):
        indices = self.treeView.selectionModel().selectedRows()
        return indices

    def connections(self):
        self.searchWidget.columnFilterIndexChanged.connect(self.proxySearch.setFilterKeyColumn)
        self.searchWidget.searchTextedChanged.connect(self.proxySearch.setFilterRegExp)
        self.reloadBtn.clicked.connect(self.refresh)
        self.treeView.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.header().customContextMenuRequested.connect(self._headerMenu)

    def setModel(self, model):
        self.model = model
        self.proxySearch.setSourceModel(model)
        if self.rowDataSource:
            self.rowDataSource.model = model
        for i in iter(self.columnDataSources):
            i.model = model
        self.treeView.setModel(self.model)

        selModel = self.treeView.selectionModel()
        selModel.selectionChanged.connect(self.selectionChanged.emit)

    def refresh(self):
        self.refreshRequested.emit()

    def contextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        indices = self.treeView.selectionModel().selectedRows()

        self.contextMenuRequested.emit(indices, menu)
        menu.exec_(self.treeView.viewport().mapToGlobal(position))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    view = TreeViewPlus()
    view.show()
    sys.exit(app.exec_())
