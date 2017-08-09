from zoo.libs.pyqt.models import delegates
from zoo.libs.pyqt.qt import QtCore, QtWidgets, QtGui



class BaseDataSource(QtCore.QObject):
    def __init__(self):
        super(BaseDataSource, self).__init__()
        self._parent = None
        self.children = []
        self.model = None

    def isRoot(self):
        """Determines if this item is the root of the tree
        :return:
        :rtype:
        """
        return True if self.parent else False

    def rowCount(self):
        """Returns the total row count for the dataSource
        :rtype: int
        """
        return 0

    def setData(self, index, value):
        """Sets the text value of this node at the specified column

        :param index: The column index
        :type index: int
        :return: the new text value for this nodes column index
        :rtype: str
        """
        pass

    def data(self, index):
        """The text for this node or column. index parameter with a value of 0 is
        the first column.

        :param index: The column index for the item
        :type index: int
        :return: the column text
        :rtype: str
        """
        return ""

    def toolTip(self, index):
        """The tooltip for the index.

        :param index: The column index for the item
        :type index: int
        :rtype: str
        """
        return ""

    def icon(self, index):
        """The icon for the index.

        :param index: The column index for the item
        :type index: int
        :rtype: QtGui.QIcon
        """
        pass

    def headerIcon(self, index):
        """Returns the column header icon

        :param index: The column index for the item
        :type index: int
        :rtype: QtGui.QIcon
        """
        return QtGui.QIcon()

    def headerText(self, index):
        """Returns the column header text

        :param index: The column index for the item
        :type index: int
        :return: the header value
        :rtype: str
        """
        return ""

    def headerVerticalText(self, index):
        """The Vertical header text, if the return type is None then no text is displayed, an empty string will
        produce a gap in the header

        :param index: The column index for the item
        :type index: int
        :rtype str or None
        """
        return None

    def headerVerticalIcon(self, index):
        """The Vertical header icon

        :param index: The column index for the item
        :type index: int
        :rtype: QtGui.QIcon()
        """
        return QtGui.QIcon()

    def isEditable(self, index):
        """Determines if this node can be editable e.g set text. Defaults to False

        :param index: The column index for the item
        :type index: int
        :return: whether or not this node is editable, defaults to False
        :rtype: bool
        """
        return False

    def isEnabled(self, index):
        """Determines if this node is enabled

        :param index: The column index for the item
        :type index: int
        :return: whether or not this node is enabled, defaults to True
        :rtype: bool
        """
        return True

    def supportsDrag(self, index):
        return False

    def supportsDrop(self, index):
        return False

    def mimeTypes(self):
        pass

    def mimeData(self, indices):
        return QtCore.QMimeData()

    def dropMimeData(self, index):
        return False

    def mimeText(self, index):
        return

    def isSelectable(self, index):
        return True

    def foregroundColor(self, index):
        return None

    def backgroundColor(self, index):
        return None

    def alignment(self, index):
        return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

    def font(self, index):
        return

    def isCheckable(self, index):
        return

    def insertRowDataSources(self, index, count):
        return None

    def insertColumnDataSources(self, index, count):
        return None

    def removeRowDataSource(self, index):
        return False

    def removeRowDataSources(self, index, count):
        return False

    def insertRowDataSource(self, index):
        return False

    def onVerticalHeaderSelection(self, index):
        """Triggered by the table view(if this source is attached to one) when the vertical header is clicked
        :param index: the row index
        :type index: int
        """
        pass

    def userObject(self, index):
        return None

    def contextMenu(self, indices, menu):
        pass

    def append(self, item):
        """Given another Node instance add it as a child.
        :param item: The child item to add, the child must already have this node as a parent.
        :type item: Node instance
        :rtype: None
        """
        if item not in self.children:
            self.children.append(item)
            item.parent = self

    def extend(self, items):
        for i in iter(items):
            if i not in self.children:
                self.children.append(i)
                i.parent = self

    def insertChild(self, index, item=None):
        """To support arbitrary child class types we allow the parameter "item" however if its None then a empty child
        of the current class type is created
        :param index: the index to insert the child
        :type index: int
        :param item: The child node if any, if None is provided then the current class Type is used
        :type item: Node
        :return: The new child is returned
        :rtype: Node
        """
        if item is None:
            item = self.__class__()

        self.children.insert(index, item)
        item.parent = self
        return item

    def remove(self, item):
        """Remove the child node
        :param item: the item to remove
        :type item: Node
        :return: True if child was removed
        :rtype: bool
        """
        try:
            item.parent = None
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
            child = self.children.pop(position)
            child.parent = None
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


class ColumnDataSource(BaseDataSource):
    def __init__(self):
        super(ColumnDataSource, self).__init__()

    def setData(self, rowDataSource, index, value):
        """Sets the text value of this node at the specified column

        :param index:
        :type index: int
        :return: the new text value for this nodes column index
        :rtype: str
        """
        pass

    def data(self, rowDataSource, index):
        """The text for this node or column. index parameter with a value of 0 is
        the first column

        :param index: The column index for the text
        :type index: int
        :return: the column text
        :rtype: str
        """
        return ""

    def toolTip(self, rowDataSource, index):
        """The tooltip for this node

        :rtype: str
        """
        return ""

    def icon(self, rowDataSource, index):
        """The icon for this node
        :rtype: QtGui.QIcon
        """
        pass

    def isCheckable(self, rowDataSource, index):
        pass

    def isEditable(self, rowDataSource, index):
        """Determines if this node can be editable e.g set text. Defaults to False
        :param index: the column index
        :type index: int
        :return: whether or not this node is editable, defaults to False
        :rtype: bool
        """
        return False

    def isEnabled(self, rowDataSource, index):
        """Determines if this node is enabled

        :param index: the column index
        :type index: int
        :return: whether or not this node is enabled, defaults to True
        :rtype: bool
        """
        return True

    def supportsDrag(self, rowDataSource, index):
        return False

    def supportsDrop(self, rowDataSource, index):
        return False

    def mimeData(self, rowDataSource, index):
        return QtCore.QMimeData()

    def dropMimeData(self, rowDataSource, index):
        return False

    def mimeText(self, rowDataSource, index):
        return

    def isSelectable(self, rowDataSource, index):
        return True

    def foregroundColor(self, rowDataSource, index):
        return None

    def backgroundColor(self, rowDataSource, index):
        return None

    def alignment(self, rowDataSource, index):
        return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter

    def font(self, rowDataSource, index):
        return


class RowDoubleDataSource(BaseDataSource):
    def delegate(self, parent):
        return delegates.NumericDoubleDelegate(parent)

    def minimum(self, index):
        return -99999.0

    def maximum(self, index):
        return 99999.0


class RowIntNumericDataSource(BaseDataSource):
    def delegate(self, parent):
        return delegates.NumericIntDelegate(parent)

    def minimum(self, index):
        return -99999

    def maximum(self, index):
        return 99999


class RowEnumerationDataSource(BaseDataSource):
    def delegate(self, parent):
        return delegates.EnumerationDelegate(parent)

    def enums(self, index):
        return []


class RowBooleanDataSource(ColumnDataSource):
    def isCheckable(self, rowDataSource, index):
        return False


class ColumnDoubleDataSource(ColumnDataSource):
    def delegate(self, parent):
        return delegates.NumericDoubleDelegate(parent)

    def minimum(self, rowDataSource, index):
        return -99999.0

    def maximum(self, rowDataSource, index):
        return 99999.0


class ColumnIntNumericDataSource(ColumnDataSource):
    def delegate(self, parent):
        return delegates.NumericIntDelegate(parent)

    def minimum(self, rowDataSource, index):
        return -99999

    def maximum(self, rowDataSource, index):
        return 99999


class ColumnEnumerationDataSource(ColumnDataSource):
    def delegate(self, parent):
        return delegates.EnumerationDelegate(parent)

    def enums(self, rowDataSource, index):
        return []