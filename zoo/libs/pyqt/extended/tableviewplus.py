from qt import QtWidgets, QtCore
from zoo.libs.pyqt.models import sortmodel
from zoo.libs.pyqt.extended import viewfilterwidget
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
        self.searchWidget.setVisibilityItems(self.rowDataSource.headerText(0))

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
        visItems = []
        for i, source in enumerate(self.columnDataSources):
            visItems.append(source.headerText(i))
        self.searchWidget.setVisibilityItems([self.rowDataSource.headerText(0)]+visItems)

    def setSearchable(self, value):
        self.searchWidget.setVisible(value)

    def _setupFilter(self):
        self.reloadBtn = QtWidgets.QToolButton(parent=self)
        self.reloadBtn.setIcon(iconlib.icon("reload"))
        self.searchLayout = QtWidgets.QHBoxLayout(self)
        self.searchLayout.setContentsMargins(2, 2, 2, 2)
        self.searchLayout.addWidget(self.reloadBtn)
        # setup the column search widget
        self.searchWidget = viewfilterwidget.ViewSearchWidget(parent=self)
        self.searchLayout.addWidget(self.searchWidget)
        self.mainLayout.addLayout(self.searchLayout)


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

        self.proxySearch = sortmodel.TableFilterProxyModel()
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
        #self.searchWidget.searchTextedCleared.connect(self.searchEdit.clear)
        self.searchWidget.columnFilterIndexChanged.connect(self.onSearchBoxChanged)
        self.searchWidget.searchTextedChanged.connect(self.proxySearch.setFilterRegExp)
        self.searchWidget.columnVisibilityIndexChanged.connect(self.toggleColumn)
        self.reloadBtn.clicked.connect(self.refresh)
        selModel = self.selectionModel()  # had to assign a var otherwise the c++ object gets deleted in PySide1
        selModel.selectionChanged.connect(self.onSelectionChanged)

    def onSelectionChanged(self, current, previous):
        indices = current.indexes()
        self.selectionChanged.emit([self._model.itemFromIndex(i) for i in indices])

    def onSearchBoxChanged(self, index, text):
        self.proxySearch.setFilterKeyColumn(index)

    def model(self):
        return self.tableview.model()

    def setModel(self, model):
        self.proxySearch.setSourceModel(model)
        self.proxySearch.setDynamicSortFilter(True)

        self._model = model
        if self.rowDataSource:
            self.rowDataSource.model = model
        for i in iter(self.columnDataSources):
            i.model = model

    def refresh(self):
        self.refreshRequested.emit()
        rowDataSource = self._model.rowDataSource
        columnDataSources = self._model.columnDataSources
        headerItems = []
        for i in xrange(len(columnDataSources)):
            headerItems.append(columnDataSources[i].headerText(i))

        self.searchWidget.setHeaderItems([rowDataSource.headerText(0)]+headerItems)

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

    def toggleColumn(self, headerText, state):
        if headerText == self.rowDataSource.headerText(0):
            if state == QtCore.Qt.Checked:
                self.tableview.showColumn(0)
            else:
                self.tableview.hideColumn(0)
        else:
            for i, source in enumerate(self.columnDataSources):
                i += 1
                if source.headerText(i) == headerText:
                    if state == QtCore.Qt.Checked:
                        self.tableview.showColumn(i)
                    else:
                        self.tableview.hideColumn(i)
