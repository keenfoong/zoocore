from qt import QtWidgets, QtCore


class ListView(QtWidgets.QListView):
    # emits the selection List as items directly from the model and the QMenu at the mouse position
    contextMenuRequested = QtCore.Signal(list, object)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent=parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenu)

    def _contextMenu(self, position):
        model = self.model()
        if model is None:
            return
        menu = QtWidgets.QMenu(self)
        selection = [model.itemFromIndex(index) for index in self.selectionModel.selectedIndexes()]
        self.contextMenuRequested.emit(selection, menu)
        menu.exec_(self.listView.viewport().mapToGlobal(position))
