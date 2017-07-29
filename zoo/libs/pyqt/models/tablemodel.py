from zoo.libs.pyqt.qt import QtCore, QtGui


class TableModel(QtCore.QAbstractTableModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    userObject = QtCore.Qt.UserRole + 2

    def __init__(self, root, parent=None):
        super(TableModel, self).__init__(parent)
        self.root = root

    def reload(self):
        """Hard reloads the model, we do this by the modelReset slot, the reason why we do this instead of insertRows()
        is because we expect that the tree structure has already been rebuilt with its children so by calling insertRows
         we would in turn create duplicates.
        """
        self.modelReset.emit()

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.root

    def itemFromIndex(self, index):
        return index.data(self.userObject) if index.isValid() else self.root

    def rowCount(self, parent):
        if parent.column() > 0 or self.root is None:
            return 0
        parentItem = self.getItem(parent)
        return parentItem.childCount()

    def columnCount(self, parent):
        if self.root is None:
            return 0
        return self.root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return item.text(column)
        elif role == QtCore.Qt.ToolTipRole:
            return item.tooltip()
        elif role == QtCore.Qt.DecorationRole:
            return item.icon()
        elif role == QtCore.Qt.BackgroundRole:
            color = item.backgroundColor(row, column)
            if color:
                return QtGui.QColor(*color)
        elif role == QtCore.Qt.ForegroundRole:
            color = item.foregroundColor(row, column)
            if color:
                return QtGui.QColor(*color)
        elif role == TableModel.sortRole:
            return item.text(column)
        elif role == TableModel.filterRole:
            return item.text(column)
        elif role == TableModel.userObject:
            return item

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        pointer = index.internalPointer()
        if role == QtCore.Qt.EditRole:
            column = index.column()
            pointer.setText(column, value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        row = index.row()
        column = index.column()
        pointer = index.internalPointer()
        flags = QtCore.Qt.ItemIsEnabled
        if pointer.isEditable(row, column):
            flags |= QtCore.Qt.ItemIsEditable
        if pointer.isSelectable(row, column):
            flags |= QtCore.Qt.ItemIsSelectable
        if pointer.isEnabled(row, column):
            flags |= QtCore.Qt.ItemIsEnabled
        return flags

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.root.headerText(section)
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self.root.headerColumnText(section)
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

        parentItem = childItem.parent()
        if parentItem == self.root or parentItem is None:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.index(), 0, parentItem)

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), item=None):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        if position < 0 or position > parentItem.childCount():
            return False

        for row in xrange(rows):
            parentItem.insertChild(position, item)
        self.endInsertRows()

        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getItem(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        success = False
        for row in xrange(rows):
            success = parentNode.remove(position)

        self.endRemoveRows()

        return success
