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
    """Main Data Model for the thumbnail widget, this is the main class to handle data access between the core and the view
    """
    # total number of items to load a time
    chunkCount = 20

    def __init__(self, parent=None):
        super(ItemModel, self).__init__(parent)
        self.rootItem = QtGui.QStandardItem('root')
        # items list , all items to show in the view should be in this one dimensional list
        self.items = []  # ::class:`item.TreeItem`
        self.loadedCount = self.chunkCount

    def canFetchMore(self, index=QtCore.QModelIndex()):
        """Overridden to handle paginating the data using the len(self.items) > self.loadedCount,

        :param index:
        :type index:
        :rtype: bool
        """

        if len(self.items) > self.loadedCount:
            return True
        return False

    def fetchMore(self, index=QtCore.QModelIndex()):
        reminder = len(self.items) - self.loadedCount
        itemsToFetch = min(reminder, self.chunkCount)
        self.beginInsertRows(QtCore.QModelIndex(), self.loadedCount, self.loadedCount + itemsToFetch-1)
        self.loadedCount += itemsToFetch
        self.endInsertRows()

    def reset(self):
        self.beginResetModel()
        self.endResetModel()

    def loadData(self):
        """Intended to be overridden by subclasses, This method should deal with loading a chunk of the items to display.
        Use self.loadedCount and self.chunkCount variable to determine the amount to load
        eg.
            if len(self.currentFilesList) < self.loadedCount:
                filesToLoad = self.mylist
            else:
                filesToLoad = self.mylist[self.loadedCount: self.loadedCount + self.chunkCount]
        :rtype: None
        """
        raise NotImplementedError()

    def data(self, index, role):
        if not index.isValid():
            return None
        row = int(index.row())
        item = self.items[row]
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return item.text(row)
        elif role == QtCore.Qt.ToolTipRole:
            return item.toolTip(row)
        elif role == QtCore.Qt.DecorationRole:
            return item.icon(row)
        elif role == QtCore.Qt.BackgroundRole:
            color = item.backgroundColor(row)
            if color:
                return QtGui.QColor(*color)
        elif role == QtCore.Qt.ForegroundRole:
            color = item.foregroundColor(row)
            if color:
                return QtGui.QColor(*color)
        return super(ItemModel, self).data(index, role)
