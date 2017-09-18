from qt import QtWidgets, QtCore


class TreeView(QtWidgets.QTreeView):
    contextMenuRequested = QtWidgets.Signal(object)

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        self.setSortingEnabled(True)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenu)

    def _contextMenu(self, pos):
        menu = QtWidgets.QMenu()
        self.contextMenuRequested.emit(menu)
        menu.exec_(self.mapToGlobal(pos))
