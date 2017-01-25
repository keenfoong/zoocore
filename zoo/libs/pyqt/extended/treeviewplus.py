from zoo.libs.pyqt.qt import QtWidgets, QtCore


class TreeViewPlus(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TreeViewPlus, self).__init__(parent)
        self._setupLayouts()
        self.rowDataModel = None
        self.columnDataModels = []
        self.model = None

    def _setupLayouts(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.filterLayout = QtWidgets.QHBoxLayout()
        self.filterLayout.setContentsMargins(2, 2, 2, 2)
        self.filterClearBtn = QtWidgets.QPushButton(">>")
        self.filterBox = QtWidgets.QLineEdit(self)
        self.treeView = QtWidgets.QTreeView()  # need to add stylesheet
        self.filterLayout.addWidget(self.filterClearBtn)
        self.filterLayout.addWidget(self.filterBox)
        self.mainLayout.addLayout(self.filterLayout)
        self.mainLayout.addWidget(self.treeView)

        self.proxyFilter = QtWidgets.QSortFilterProxyModel()
        self.proxyFilter.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.treeView.setModel(self.proxyFilter)

        self.filterClearBtn.clicked.connect(self.filterBox.clear)
        self.treeView.setSortingEnabled(True)

    def setSourceModel(self, model):
        self.proxyFilter.setSourceModel(model)
        self.filterBox.textChanged.connect(self.proxyFilter.setFilterRegExp)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    view = TreeViewPlus()
    view.show()
    sys.exit(app.exec_())
