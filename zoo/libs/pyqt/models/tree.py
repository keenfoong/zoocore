"""This module is for a standard Qt tree model
"""
from zoo.libs.pyqt.qt import QtCore


class Node(QtCore.QObject):
    """The Node class acts as a single item within a tree or DAG structure.
    All trees should have a root and at least one child node.
    """

    def __init__(self, metadata=None, parent=None):
        """We initialize the children to an empty list.
        :param parent: The parent of this node
        :type parent: Node instance
        """
        super(Node, self).__init__(parent)
        self.metadata = metadata
        self._parent = parent
        self.children = []

    def __repr__(self):
        return "{}: {}".format(self.__class__.__name__, self.tooltip())

    def setText(self, index):
        """Sets the text value of this node at the specified column
        
        :param index:
        :type index: int
        :return: the new text value for this nodes column index
        :rtype: str
        """
        pass

    def text(self, index):
        """The text for this node or column. index parameter with a value of 0 is
        the first column
        
        :param index: The column index for the text
        :type index: int
        :return: the column text
        :rtype: str
        """
        return ""

    def tooltip(self):
        """The tooltip for this node
        
        :rtype: str
        """
        return ""

    def icon(self):
        """The icon for this node
        
        :rtype: QtGui.QIcon
        """
        pass

    def columnCount(self):
        """The column count, this is only required to be set on the root node
        
        :rtype: int
        """
        return 0

    def headerText(self, index):
        """The header text, index parameter of 0 is the first column
        
        :param index: the column index
        :type index: int
        :return: the header value
        :rtype: str
        """
        return ""

    def flags(self, index):
        """Sets the node q flag states
        
        :param index: the column index
        :type index: int
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def isEditable(self, index):
        """Determines if this node can be editable e.g set text. Defaults to False
        
        :param index: the column index
        :type index: int
        :return: whether or not this node is editable, defaults to False
        :rtype: bool
        """
        return False

    def alignment(self, index):
        return QtCore.QVariant(int(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft))

    def append(self, item):
        """Given another Node instance add it as a child.
        
        :param item: The child item to add, the child must already have this node as a parent.
        :type item: Node instance
        :rtype: None
        """
        if item not in self.children:
            self.children.append(item)

    def insertChild(self, index):
        pass

    def remove(self, item):
        """Remove the child node
        
        :param item: the item to remove
        :type item: Node
        :return: True if child was removed
        :rtype: bool
        """
        try:
            self.children.remove(item)
            return True
        except:
            return False

    def removeChildren(self, position, count):
        """Removes a number of children from this node starting at a position index.
        
        :param position: the starting position(child index) to remove
        :type position: int
        :param count: the number of children to remove
        :type count: int
        :rtype: bool
        """
        if position < 0 or position + count > self.childCount():
            return False

        for row in xrange(count):
            self.children.pop(position)
        return True

    def child(self, index):
        """Return the child of this node by index
        
        :param index: the child index
        :type index: int
        :return: Returns the node instance for the child
        :rtype: Node
        """
        if index in range(len(self.children)):
            return self.children[index]

    def iterChildren(self, node):
        for n in iter(node.children):
            yield n
            for i in iter(n.children):
                yield i

    def childCount(self):
        """The number of children for this node
        
        :return: child count
        :rtype: int
        """
        return len(self.children)

    def parent(self):
        """Returns the parent of this node
        
        :rtype: Node
        """
        return self._parent

    def index(self):
        if self._parent is not None:
            return self._parent.children.index(self)

        return 0


class TreeModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    userObject = QtCore.Qt.UserRole + 2

    def __init__(self, root, parent=None):
        super(TreeModel, self).__init__(parent)
        self.root = root

    def itemFromIndex(self, index):
        return index.data(self.userObject) if index.isValid() else self.root

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        parentItem = self.getItem(parent)
        return parentItem.childCount()

    def columnCount(self, parent):
        return self.root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return item.text(index.column())
        elif role == QtCore.Qt.ToolTipRole:
            return item.tooltip()
        elif role == QtCore.Qt.DecorationRole:
            return item.icon()
        elif role == TreeModel.sortRole:
            return item.text(index.column())
        elif role == TreeModel.filterRole:
            return item.text(index.column())
        elif role == TreeModel.userObject:
            return item

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        pointer = index.internalPointer()
        if role == QtCore.Qt.EditRole:
            column = index.column()
            pointer.setText(value, column)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        pointer = index.internalPointer()
        return pointer.flags(index)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.root.headerText(section)
        return None

    def index(self, row, column, parent):
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

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        if position < 0 or position > parentItem.childCount():
            return False

        for row in range(rows):
            parentItem.insertChild(position)
        self.endInsertRows()

        return True

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.root
