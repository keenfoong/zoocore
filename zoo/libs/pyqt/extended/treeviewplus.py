from zoo.libs.pyqt.qt import QtWidgets, QtCore, QtGui


class TreeViewPlus(QtWidgets.QFrame):
    selectionChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(TreeViewPlus, self).__init__(parent)

        self._setupLayouts()
        self.model = None
        self.connections()

    def setModel(self, model):
        self.model = model
        self.treeView.setModel(self.model)
        self.refresh()

    def _setupLayouts(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.filterLayout = QtWidgets.QHBoxLayout()
        self.filterLayout.setContentsMargins(2, 2, 2, 2)
        self.filterClearBtn = QtWidgets.QPushButton(">>")
        self.filterBox = QtWidgets.QLineEdit(self)
        self.treeView = QtWidgets.QTreeView()  # need to add stylesheet
        self.treeView.setSelectionMode(self.treeView.ExtendedSelection)
        self.filterLayout.addWidget(self.filterClearBtn)
        self.filterLayout.addWidget(self.filterBox)
        self.mainLayout.addLayout(self.filterLayout)
        self.mainLayout.addWidget(self.treeView)

        self.proxyFilter = QtCore.QSortFilterProxyModel()
        self.proxyFilter.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.treeView.setModel(self.proxyFilter)
        self.treeView.setSortingEnabled(True)

    def connections(self):
        self.treeView.expanded.connect(self.refresh)
        self.treeView.collapsed.connect(self.refresh)
        self.treeView.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.filterClearBtn.clicked.connect(self.filterBox.clear)

    def setFilterModel(self, model):
        self.proxyFilter.setSourceModel(model)
        self.filterBox.textChanged.connect(self.proxyFilter.setFilterRegExp)

    def onSelectionChanged(self, *args, **kwargs):
        self.selectionChanged.emit(self.treeView.selectedIndexes())

    def refresh(self):
        for index in xrange(self.model.columnCount(QtCore.QModelIndex())):
            self.treeView.resizeColumnToContents(index)
            newWidth = self.treeView.columnWidth(index) + 10
            self.treeView.setColumnWidth(index, newWidth)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    view = TreeViewPlus()
    view.show()
    sys.exit(app.exec_())
