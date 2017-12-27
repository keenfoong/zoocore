import os

from qt import QtGui, QtCore, QtWidgets

class ThumbnailDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super(ThumbnailDelegate, self).__init__(parent)

    def sizeHint(self, option, index):
        return index.model().itemFromIndex(index).sizeHint()

    def paint(self, painter, options, index):
        index.model().itemFromIndex(index).paint(painter, options, index)

class ItemModel(QtGui.QStandardItemModel):
    # total number of items to load a time
    _chunkCount = 20

    def __init__(self):
        super(ItemModel, self).__init__()
        self.items = []
        self.loadedCount = 0

    def canFetchMore(self, index=QtCore.QModelIndex()):
        if len(self.items) > self.loadedCount:
            return True
        return False

    def fetchMore(self, index=QtCore.QModelIndex()):
        reminder = len(self.items) - self.loadedCount
        itemsToFetch = min(reminder, self.loadedCount)
        self.beginInsertRows(QtCore.QModelIndex(), self.loadedCount, self.loadedCount + itemsToFetch - 1)
        self.loadedCount += itemsToFetch
        self.endInsertRows()

    def reset(self):
        self.beginResetModel()
        self.endResetModel()

    def loadData(self):
        raise NotImplementedError()


