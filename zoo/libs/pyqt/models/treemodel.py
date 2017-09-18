"""This module is for a standard Qt tree model
"""
from qt import QtCore, QtGui


class TreeModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    userObject = QtCore.Qt.UserRole + 2

    def __init__(self, root, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = root

    def reload(self):
        """Hard reloads the model, we do this by the modelReset slot, the reason why we do this instead of insertRows()
        is because we expect that the tree structure has already been rebuilt with its children so by calling insertRows
         we would in turn create duplicates.
        """
        self.modelReset.emit()

    def itemFromIndex(self, index):
        return index.data(self.userObject) if index.isValid() else self.root

    def rowCount(self, parent):
        if parent.column() > 0 or self.root is None:
            return 0
        parentItem = self.getItem(parent)
        return parentItem.rowCount()

    def columnCount(self, parent):
        if self.root is None:
            return 0
        return self.root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        column = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return item.data(column)
        elif role == QtCore.Qt.ToolTipRole:
            return item.toolTip(column)
        elif role == QtCore.Qt.DecorationRole:
            return item.icon(column)

        elif role == QtCore.Qt.BackgroundRole:
            color = item.backgroundColor(column)
            if color:
                return QtGui.QColor(*color)
        elif role == QtCore.Qt.ForegroundRole:
            color = item.foregroundColor(column)
            if color:
                return QtGui.QColor(*color)
        elif role == QtCore.Qt.FontRole:
            return item.font(column)
        elif role == TreeModel.sortRole:
            return item.text(column)
        elif role == TreeModel.filterRole:
            return item.text(column)
        elif role == TreeModel.userObject:
            return item

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        pointer = index.internalPointer()
        if role == QtCore.Qt.EditRole:
            column = index.column()
            pointer.setData(column, value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        column = index.column()
        pointer = index.internalPointer()
        flags = QtCore.Qt.ItemIsEnabled
        if pointer.supportsDrag(column):
            flags |= QtCore.Qt.ItemIsDragEnabled
        if pointer.supportsDrop(column):
            flags |= QtCore.Qt.ItemIsDropEnabled
        if pointer.isEditable(column):
            flags |= QtCore.Qt.ItemIsEditable
        if pointer.isSelectable(column):
            flags |= QtCore.Qt.ItemIsSelectable
        if pointer.isEnabled(column):
            flags |= QtCore.Qt.ItemIsEnabled
        return flags

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.root.headerText(section)
        return None

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()

        parentItem = childItem.parentSource()
        if parentItem == self.root or parentItem is None:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.index(), 0, parentItem)

    def insertRow(self, position, parent=QtCore.QModelIndex(), **kwargs):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position)
        if position < 0 or position > len(parentItem.children):
            return False
        parentItem.insertRowDataSource(position, **kwargs)
        self.endInsertRows()

        return True

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), **kwargs):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        if position < 0 or position > len(parentItem.children):
            return False
        result = parentItem.insertRowDataSources(int(position), int(rows), **kwargs)

        self.endInsertRow()

        return result

    def removeRows(self, position, rows, parent=QtCore.QModelIndex(), **kwargs):
        parentNode = self.getItem(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        if position < 0 or position > len(parentNode.children):
            return False
        result = parentNode.insertRowDataSources(int(position), int(rows), **kwargs)

        self.endRemoveRows()

        return result

    def removeRow(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getItem(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        if position < 0 or position > len(parentNode.children):
            return False

        success = parentNode.removeRowDataSource(position)

        self.endRemoveRows()

        return success

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.root