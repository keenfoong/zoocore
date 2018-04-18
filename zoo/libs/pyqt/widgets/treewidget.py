
from zoo.libs.pyqt.embed import mayaui
from qt import QtCore, QtWidgets, QtGui

class TreeWidgetFrame(QtWidgets.QWidget):
    def __init__(self, parent=None, title=""):
        super(TreeWidgetFrame, self).__init__(parent=parent)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.title = QtWidgets.QLabel(title, parent=parent)
        self.searchEdit = QtWidgets.QLineEdit(parent=parent)
        self.treeWidget = None
        self.toolbarLayout = QtWidgets.QHBoxLayout()


    def initUi(self, treeWidget):
        """
        Initialize Ui
        :return:
        """
        self.treeWidget = treeWidget
        self.setupToolbar()
        self.mainLayout.setContentsMargins(2, 4, 2, 4)

        self.mainLayout.addWidget(self.title)
        self.mainLayout.addLayout(self.toolbarLayout)
        self.mainLayout.addWidget(self.treeWidget)

        self.setLayout(self.mainLayout)

    def setupToolbar(self):
        """
        The toolbar for the ComponentTreeView which will have widgets such as the searchbar,
        and other useful buttons.
        :return:
        """

        self.toolbarLayout.setContentsMargins(0, 0, 0, 0)
        self.toolbarLayout.addWidget(self.searchEdit)

        self.searchEdit.setPlaceholderText("Search...")

        line = QtWidgets.QFrame(parent=self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.toolbarLayout.addWidget(line)

        return self.toolbarLayout

    def connections(self):
        self.searchEdit.textChanged.connect(self.onSearchChanged)

    def onSearchChanged(self):
        """
        Filter the results based on the text inputted into the search bar
        :return:
        """

        if self.treeWidget is not None:
            text = self.searchEdit.text().lower()
            self.treeWidget.filter(text)
            self.treeWidget.updateTreeWidget()

    def addGroup(self, name="", expanded=True):
        if self.treeWidget is not None:
            return self.treeWidget.addGroup(name, expanded=expanded)
        else:
            print("TreeWidgetFrame.addGroup(): TreeWidget shouldn't be None!")

    def updateTreeWidget(self):
        if self.treeWidget is not None:
            self.treeWidget.updateTreeWidget()


class TreeWidget(QtWidgets.QTreeWidget):
    """
    A custom tree widget with some default things we want in zoo
    """

    ITEMTYPE_WIDGET = "WIDGET"
    ITEMTYPE_GROUP = "GROUP"

    WIDGET_COL = 0
    DATA_COL = 2

    def __init__(self, parent=None, locked=False):
        super(TreeWidget, self).__init__(parent)

        self.defaultGroupName = "Group"

        self.font = QtGui.QFont("sans", mayaui.dpiScale(11))

        self.groupDraggableFlags = QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        self.componentDraggableFlags = QtCore.Qt.ItemIsDragEnabled

        self.groupFlags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

        self.componentFlags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled

        self.setLocked(locked)

        self.initUi()

    def setLocked(self, locked):

        if locked:
            self.groupFlags = self.groupFlags & ~self.groupDraggableFlags
            self.componentFlags = self.componentFlags & ~self.componentDraggableFlags
        else:
            self.groupFlags = self.groupFlags | self.groupDraggableFlags
            self.componentFlags = self.componentFlags | self.componentDraggableFlags

        pass

    def initUi(self):
        # Header setup
        self.headerItem = QtWidgets.QTreeWidgetItem(["Widget"])
        self.setHeaderItem(self.headerItem)
        self.header().hide()

        self.initDragDrop()

        #self.setStyleSheet("QTreeWidgetItem {self.font-color: black}")

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

    def dropEvent(self, event):
        """
        The drop event when dragging a ComponentWidget from one place to another
        :param event:
        :return:
        """
        dragged = self.currentItem()
        wgt = self.itemWidget(dragged)

        # We have to recreate the componentWidgetItem, because PySide destroys everything on dropEvent.
        # If you do a straight reference change, it crashes
        newWgt = wgt.copy()

        super(TreeWidget, self).dropEvent(event)
        newWgt.setParent(self)  # parent must be put here otherwise it will crash

        self.setItemWidget(dragged, self.WIDGET_COL, newWgt)
        self.updateTreeWidget()

    def addNewItem(self, name, widget=None, itemType=ITEMTYPE_WIDGET):
        """
        Add a new item type. Should be a group or an itemWidget
        :param name:
        :param widget:
        :param itemType:
        :return:
        """

        if itemType == self.ITEMTYPE_WIDGET:
            flags = self.componentFlags
        else:
            flags = self.groupFlags

        newTreeItem = TreeWidgetItem(self, strings=[name, ""], font=self.font, flags=flags)
        newTreeItem.setData(self.DATA_COL, QtCore.Qt.EditRole, itemType)  # Data set to column 2, which is not visible
        newTreeItem.setFont(self.WIDGET_COL, self.font)

        if widget:
            widget.setParent(self)

        if itemType == self.ITEMTYPE_WIDGET:
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

    def addGroup(self, name="", expanded=True, groupSelected=True):
        """
        Adds a group to the ComponentTreeWidget. If no name is given, it will generate a unique one
        in the form of "Group 1", "Group 2", "Group 3" etc

        TODO: This area still needs a bit of work
        :param expanded:
        :param name:
        :return:
        """

        # Place group after last selected item
        if len(self.selectedItems()) > 0:
            index = self.indexFromItem(self.selectedItems()[-1]).row()+1
        else:
            # Otherwise just place it on the top
            index = self.topLevelItemCount()

        name = name or self.getUniqueGroupName()
        group = self.addNewItem(name, None, self.ITEMTYPE_GROUP)
        self.insertTopLevelItem(index, group)

        if groupSelected:
            for s in self.selectedItems():
                # If its a group move on to the next one
                if self.getItemType(s) == self.ITEMTYPE_GROUP:
                    continue

                self.addToGroup(s, group, updateTree=False)

        group.setExpanded(expanded)

        self.updateTreeWidget()

        return group

    def addToGroup(self, item, group, updateTree=True):
        newWgt = self.itemWidget(item, self.WIDGET_COL).copy()

        if item.parent() is None:
            # If it is a top level item
            index = self.indexFromItem(item).row()
            self.takeTopLevelItem(index)
        else:
            # If its under a group
            index = item.parent().indexOfChild(item)
            item.parent().takeChild(index)

        # add to the last
        group.addChild(item)
        newWgt.setParent(self)  # parent must be put here otherwise it will crash
        self.setItemWidget(item, 0, newWgt)

        if updateTree:
            self.updateTreeWidget()

    def getUniqueGroupName(self):
        """
        Returns a unique group name: "Group 1", "Group 2", "Group 3" etc.
        :return:
        """
        num = len(self.findItems(self.defaultGroupName + " *", QtCore.Qt.MatchFlag.MatchWildcard, 0))
        return self.defaultGroupName + " " + str(num+1)



class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, strings, font, flags):
        super(TreeWidgetItem, self).__init__(parent, strings)
        self.setFont(1, font)
        self.setFlags(flags)
