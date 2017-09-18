from qt import QtWidgets, QtCore
from zoo.libs import iconlib


class TableViewPlus(QtWidgets.QFrame):
    selectionChanged = QtCore.Signal(object)
    contextMenuRequested = QtCore.Signal(list, object)
    refreshRequested = QtCore.Signal()

    def __init__(self, searchable=False, parent=None):
        super(TableViewPlus, self).__init__(parent)

        self._setupLayouts()
        self._model = None
        self.connections()
        self.setSearchable(searchable)
        self.rowDataSource = None
        self.columnDataSources = []

    def registerRowDataSource(self, dataSource):
        self.rowDataSource = dataSource
        if hasattr(dataSource, "delegate"):
            delegate = dataSource.delegate(self.tableview)
            self.tableview.setItemDelegateForColumn(0, delegate)

        self.rowDataSource.model = self._model
        self._model.rowDataSource = dataSource
        self.tableview.verticalHeader().sectionClicked.connect(self.rowDataSource.onVerticalHeaderSelection)

    def registerColumnDataSources(self, dataSources):
        if not self.rowDataSource:
            raise ValueError("Must assign rowDataSource before columns")
        self.columnDataSources = dataSources
        for i in xrange(len(dataSources)):
            source = dataSources[i]
            source.model = self._model
            if hasattr(source, "delegate"):
                delegate = source.delegate(self.tableview)
                self.tableview.setItemDelegateForColumn(i + 1, delegate)

        self._model.columnDataSources = dataSources

    def setSearchable(self, value):
        self.searchFrame.setVisible(value)

    def _setupFilter(self):
        self.searchBoxLabel = QtWidgets.QLabel("Search By: ", parent=self)
        self.searchHeaderBox = QtWidgets.QComboBox(parent=self)

        self.searchFrame = QtWidgets.QFrame(parent=self)
        self.searchFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.searchFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.reloadBtn = QtWidgets.QToolButton(parent=self)
        self.reloadBtn.setIcon(iconlib.icon("reload"))
        self.searchLayout = QtWidgets.QHBoxLayout(self)
        self.searchLayout.setContentsMargins(2, 2, 2, 2)
        self.searchClearBtn = QtWidgets.QPushButton("Clear", parent=self)
        self.searchLabel = QtWidgets.QLabel("Search", parent=self)
        self.searchEdit = QtWidgets.QLineEdit(self)
        self.searchFrame.setLayout(self.searchLayout)
        self.searchLayout.addWidget(self.reloadBtn)
        self.searchLayout.addWidget(self.searchBoxLabel)
        self.searchLayout.addWidget(self.searchHeaderBox)
        self.searchLayout.addWidget(self.searchLabel)
        self.searchLayout.addWidget(self.searchEdit)
        self.searchLayout.addWidget(self.searchClearBtn)
        self.mainLayout.addWidget(self.searchFrame)

    def _setupLayouts(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.tableview = QtWidgets.QTableView(parent=self)
        self.tableview.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tableview.setSelectionMode(self.tableview.ExtendedSelection)
        self.tableview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableview.customContextMenuRequested.connect(self.contextMenu)
        self._setupFilter()

        self.mainLayout.addWidget(self.tableview)

        self.proxySearch = QtCore.QSortFilterProxyModel(parent=self)
        self.proxySearch.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxySearch.setFilterKeyColumn(0)
        self.tableview.setModel(self.proxySearch)
        self.tableview.setSortingEnabled(True)
        self.tableview.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tableview.setShowGrid(False)
        self.tableview.setAlternatingRowColors(True)
        self.tableview.horizontalHeader().setStretchLastSection(True)

    def selectionModel(self):
        return self.tableview.selectionModel()

    def connections(self):
        self.searchClearBtn.clicked.connect(self.searchEdit.clear)
        self.searchHeaderBox.currentIndexChanged.connect(self.onSearchBoxChanged)
        self.reloadBtn.clicked.connect(self.refresh)
        self.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.searchEdit.textChanged.connect(self.proxySearch.setFilterRegExp)

    def onSelectionChanged(self, current, previous):
        indices = current.indexes()
        self.selectionChanged.emit([self._model.itemFromIndex(i) for i in indices])

    def onSearchBoxChanged(self):
        index = self.searchHeaderBox.currentIndex()
        self.proxySearch.setFilterKeyColumn(index)

    def setModel(self, model):
        self.proxySearch.setSourceModel(model)
        self.proxySearch.setDynamicSortFilter(True)
        self.proxySearch.setSortRole(QtCore.Qt.DisplayRole)
        self.proxySearch.setFilterRole(QtCore.Qt.DisplayRole)
        self.proxySearch.setFilterKeyColumn(0)

        self._model = model
        if self.rowDataSource:
            self.rowDataSource.model = model
        for i in iter(self.columnDataSources):
            i.model = model
        self.tableview.setModel(self._model)

    def refresh(self):
        self.refreshRequested.emit()
        rowDataSource = self._model.rowDataSource
        self.searchHeaderBox.addItem(rowDataSource.headerText(0))
        columnDataSources = self._model.columnDataSources
        for i in xrange(len(columnDataSources)):
            self.searchHeaderBox.addItem(columnDataSources[i].headerText(i))

    def contextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        selection = self.selectedRows()
        if self.rowDataSource:
            self.rowDataSource.contextMenu(selection, menu)
        self.contextMenuRequested.emit(selection, menu)
        menu.exec_(self.tableview.viewport().mapToGlobal(position))

    def selectedRows(self):
        """From all the selectedIndices grab the row numbers, this use selectionModel.selectedIndexes() to pull the rows
        out
        :return: A list of row numbers
        :rtype: list(int)
        """
        return list(set([i.row() for i in self.selectionModel().selectedIndexes()]))

    def selectedColumns(self):
        return list(set([i.column() for i in self.selectionModel().selectedColumns()]))
