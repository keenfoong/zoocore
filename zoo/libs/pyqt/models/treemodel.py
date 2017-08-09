"""This module is for a standard Qt tree model
"""
from zoo.libs.pyqt.qt import QtCore, QtGui


class TreeModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    userObject = QtCore.Qt.UserRole + 2

    def __init__(self, parent=None):
        """first element is the rowDataSource
        :param parent:
        :type parent:
        """
        super(TreeModel, self).__init__(parent=parent)
        self._rowDataSource = None
        self.columnDataSources = []

    @property
    def rowDataSource(self):
        return self._rowDataSource

    @rowDataSource.setter
    def rowDataSource(self, source):
        self._rowDataSource = source

    def columnDataSource(self, index):
        if not self._rowDataSource or not self.columnDataSources:
            return

        return self.columnDataSources[index - 1]

    def dataSource(self, index):
        if index == 0:
            return self._rowDataSource
        return self.columnDataSources[index - 1]

    def reload(self):
        """Hard reloads the model, we do this by the modelReset slot, the reason why we do this instead of insertRows()
        is because we expect that the tree structure has already been rebuilt with its children so by calling insertRows
         we would in turn create duplicates.
        """
        self.modelReset.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):

        if parent.column() > 0 or self._rowDataSource is None:
            return 0
        return self.rowDataSource.childCount()

    def columnCount(self, parent):
        if not self._rowDataSource or not self.columnDataSources:
            return 0
        return len(self.columnDataSources) + 1

    def data(self, index, role):
        if not index.isValid():
            return None

        column = int(index.column())
        row = int(index.row())
        dataSource = self.dataSource(column)
        if dataSource is None:
            return
        if column == 0:
            kwargs = {"index": row}
        else:
            kwargs = {"rowDataSource": self._rowDataSource,
                      "index": row}
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return dataSource.data(**kwargs)
        elif role == QtCore.Qt.ToolTipRole:
            return dataSource.toolTip(**kwargs)
        elif role == QtCore.Qt.DecorationRole:
            return dataSource.icon(**kwargs)
        elif role == QtCore.Qt.CheckStateRole and dataSource.isCheckable(**kwargs):
            if dataSource.isCheckable(**kwargs):
                return QtCore.Qt.Checked
            return QtCore.Qt.Unchecked
        elif role == QtCore.Qt.TextAlignmentRole:
            return dataSource.alignment(**kwargs)
        elif role == QtCore.Qt.BackgroundRole:
            color = dataSource.backgroundColor(**kwargs)
            if color:
                return QtGui.QColor(*color)
        elif role == QtCore.Qt.ForegroundRole:
            color = dataSource.foregroundColor(**kwargs)
            if color:
                return QtGui.QColor(*color)
        elif role == TreeModel.sortRole:
            return dataSource.data(**kwargs)
        elif role == TreeModel.filterRole:
            return dataSource.data(**kwargs)
        elif role == TreeModel.userObject:
            return dataSource.userObject(row)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid() or not self._rowDataSource:
            return False
        if role == QtCore.Qt.EditRole:
            column = index.column()

            if column == 0:
                self._rowDataSource.setData(index.row(), value)
            else:
                self.columnDataSources[column - 1].setData(self._rowDataSource, index.row(), value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def flags(self, index):
        if not index.isValid() or not self._rowDataSource:
            return QtCore.Qt.NoItemFlags
        row = index.row()
        column = index.column()
        dataSource = self.dataSource(column)
        flags = QtCore.Qt.ItemIsEnabled
        if column == 0:
            kwargs = {"index": row}
            if dataSource.supportsDrag(**kwargs):
                flags |= QtCore.Qt.ItemIsDragEnabled
            if dataSource.supportsDrop(*kwargs):
                flags |= QtCore.Qt.ItemIsDropEnabled
        else:
            kwargs = {"rowDataSource": self._rowDataSource,
                      "index": row}
        if dataSource.isCheckable(**kwargs):
            flags |= QtCore.Qt.ItemIsUserCheckable
        if dataSource.isEditable(**kwargs):
            flags |= QtCore.Qt.ItemIsEditable
        if dataSource.isSelectable(**kwargs):
            flags |= QtCore.Qt.ItemIsSelectable
        if dataSource.isEnabled(**kwargs):
            flags |= QtCore.Qt.ItemIsEnabled

        return flags

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            dataSource = self.dataSource(section)
            if role == QtCore.Qt.DisplayRole:
                return dataSource.headerText(section)
            elif role == QtCore.Qt.DecorationRole:
                icon = dataSource.headerIcon(section)
                if icon.isNull:
                    return
                return icon.pixmap(icon.availableSizes()[-1])
        return None

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        parent = self._rowDataSource.parent
        if not parent:
            return QtCore.QModelIndex()
        child = parent().child(row)
        if child:
            return self.createIndex(row, column, child)
        return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childDataSource = index.internalPointer()
        if not childDataSource:
            return QtCore.QModelIndex()
        parentDataSource = childDataSource.parent()
        if parentDataSource == self._rowDataSource or parentDataSource is None:
            return QtCore.QModelIndex()

        return self.createIndex(parentDataSource.index(), 0, parentDataSource)

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), **kwargs):
        if not parent.isValid():
            return False
        parentDataSource = parent.internalPointer()
        self.beginInsertRows(parent, position, position + rows - 1)
        if position < 0 or position > parentDataSource.childCount():
            return False
        result = parentDataSource.inserRowDataSources(position, **kwargs)
        self.endInsertRows()

        return result

    def removeRows(self, position, rows, parent=QtCore.QModelIndex(), **kwargs):
        if not parent.isValid():
            return False
        parentDataSource = parent.internalPointer()
        self.beginRemoveRows(parent, position, position + rows - 1)
        result = parentDataSource.removeRowDataSources(int(position), **kwargs)
        self.endRemoveRows()

        return result
