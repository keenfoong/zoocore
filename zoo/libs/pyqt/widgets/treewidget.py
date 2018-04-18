
from zoo.libs.pyqt.embed import mayaui
from qt import QtCore, QtWidgets, QtGui


class TreeWidget(QtWidgets.QTreeWidget):
    """
    A custom tree widget with some default things we want in zoo
    """
    def __init__(self, parent=None):
        self.WIDGET_COL = 0
        self.DATA_COL = 2

        self.ITEMTYPE_WIDGET = "WIDGET"
        self.ITEMTYPE_GROUP = "GROUP"

        super(TreeWidget, self).__init__(parent)

        self.font = QtGui.QFont("sans", mayaui.dpiScale(11))

        self.groupFlags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | \
                          QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        self.componentFlags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled

        self.initUi()

    def initUi(self):
        # Header setup
        self.headerItem = QtWidgets.QTreeWidgetItem(["Widget"])
        self.setHeaderItem(self.headerItem)
        self.header().hide()

        self.initDragDrop()

        self.setStyleSheet("QTreeWidgetItem {self.font-color: black}"
                           "QTreeWidget::item {padding: 3px 2px;}")
        self.resizeColumnToContents(1)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setIndentation(mayaui.dpiScale(10))
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def initDragDrop(self):
        # Drag drop settings
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

    def addNewItem(self, widget, name, itemType):
        newTreeItem = TreeWidgetItem(self, strings=[name, ""], font=self.font, flags=self.componentFlags)
        widget.setParent(self)
        newTreeItem.setData(self.DATA_COL, QtCore.Qt.EditRole, itemType)  # Data set to column 2, which is not visible
        self.setItemWidget(newTreeItem, self.WIDGET_COL, widget)  # items parent must be set otherwise it will crash

        return newTreeItem

    def itemWidgets(self, group=None):
        """
        Gets all the item widgets in group. If group is none, then get the root level
        :return:
        """

        treeItem = group or self.invisibleRootItem()
        widgets = []

        for i in range(treeItem.childCount()):
            child = treeItem.child(i)
            # Recursively go through the tree and apply the filter
            if child.childCount() > 0:
                widgets.extend(self.componentWidgets(child))

            if self.getItemType(child) == self.ITEMTYPE_WIDGET:
                wgt = self.getComponentWidget(child)
                widgets.append(wgt)

        return widgets

    def itemWidget(self, treeItem, col=None):
        """
        Short hand to get the item widget from the default column (as defined by self.WIDGET_COL)
        :param treeItem:
        :param col:
        :return:
        """
        col = col or self.WIDGET_COL

        return super(TreeWidget, self).itemWidget(treeItem, col)

    def updateTreeWidget(self):
        """
        Updates the tree widget so the row heights of the TreeWidgetItems matches what the ComponentWidgets ask for
        in terms of the sizeHint() asks for
        :return:
        """
        # Super hacky way to update the TreeWidget, add an empty object and then remove it
        self.insertTopLevelItem(0, QtWidgets.QTreeWidgetItem())
        self.takeTopLevelItem(0)  # Must be a better way to do this

    def getItemType(self, treeItem):
        """
        Get the item type ("COMPONENT" or "GROUP")

        :param treeItem: The TreeWidgetItem to get the type of
        :type treeItem: TreeWidgetItem
        :return:
        """
        return treeItem.data(self.DATA_COL, QtCore.Qt.EditRole)

    def getItemName(self, treeItem):
        itemType = self.getItemType(treeItem)

        if itemType == self.ITEMTYPE_WIDGET:
            return self.itemWidget(treeItem, self.WIDGET_COL).name
        elif itemType == self.ITEMTYPE_GROUP:
            return treeItem.text(self.WIDGET_COL)

    def filter(self, text, item=None):
        filterItem = item or self.invisibleRootItem()

        for i in range(filterItem.childCount()):
            child = filterItem.child(i)
            # Recursively go through the tree and apply the filter
            if child.childCount() > 0:
                self.filter(text, child)

            name = self.getItemName(child)
            print(text, name)
            found = (text in name.lower())
            self.setItemHidden(child, not found)

            #for i in range(self.rowCount()):
            #    found = not (text in self.cellWidget(i, 0).getTitle().lower())
            #    self.setRowHidden(i, found)



class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, strings, font, flags):
        super(TreeWidgetItem, self).__init__(parent, strings)
        self.setFont(1, font)
        self.setFlags(flags)
