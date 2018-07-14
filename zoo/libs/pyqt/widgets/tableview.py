from qt import QtWidgets, QtCore


class TableView(QtWidgets.QTableView):
    contextMenuRequested = QtCore.Signal()

    def __init__(self, parent):
        super(TableView, self).__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSelectionMode(self.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuRequested.emit)
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)

    def commitData(self, editor):
        theModel = self.currentIndex().model()
        data = theModel.data(self.currentIndex(), QtCore.Qt.EditRole)

        for index in self.selectedIndexes():
            if index == self.currentIndex():
                continue
            # Supply None as the value
            self.model().setData(index, data, QtCore.Qt.EditRole)
        super(TableView, self).commitData(editor)
