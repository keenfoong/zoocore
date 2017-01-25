from zoo.libs.pyqt.qt import QtWidgets, QtCore


class ListView(QtWidgets.QListView):
    contextMenuRequested = QtWidgets.Signal(object)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent=parent)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenu)

    def _contextMenu(self, pos):
        menu = QtWidgets.QMenu()
        self.contextMenuRequested.emit(menu)
        menu.exec_(self.mapToGlobal(pos))
