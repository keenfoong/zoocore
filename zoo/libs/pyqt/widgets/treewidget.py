from zoo.libs.pyqt.embed import mayaui
from qt import QtCore, QtWidgets, QtGui
from zoo.apps.hiveartistui import tooltips
from zoo.libs import iconlib


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
        self.toolbarLayout.setSpacing(1)
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

    ADD_INSERTAFTER = 0
    ADD_INSERTEND = 1

    def __init__(self, parent=None, locked=False, allowSubGroups=True):
        super(TreeWidget, self).__init__(parent)

        self.defaultGroupName = "Group"

        self.font = QtGui.QFont("sans", mayaui.dpiScale(9))
        self.allowSubGroups = allowSubGroups

        self.groupFlags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        self.groupUnlockedFlags = QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

        self.itemWidgetFlags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled
        self.itemWidgetUnlockedFlags = QtCore.Qt.ItemIsDragEnabled

        self.locked = locked
        self.setLocked(locked)

        self.initUi()

    def setLocked(self, locked):
        self.locked = locked

        if locked:
            self.groupFlags = self.groupFlags & ~self.groupUnlockedFlags
            self.itemWidgetFlags = self.itemWidgetFlags & ~self.itemWidgetUnlockedFlags
        else:
            self.groupFlags = self.groupFlags | self.groupUnlockedFlags
            self.itemWidgetFlags = self.itemWidgetFlags | self.itemWidgetUnlockedFlags

        self.applyFlags()

    def initUi(self):
        # Header setup
        self.headerItem = QtWidgets.QTreeWidgetItem(["Widget"])
        self.setHeaderItem(self.headerItem)
        self.header().hide()

        self.initDragDrop()

        # self.setStyleSheet("QTreeWidgetItem {self.font-color: black}")

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

        # Check if the target item is a group, if subgroups aren't allowed just return
        targetItem = self.itemAt(event.pos())

        dragged = self.currentItem()
        wgt = self.itemWidget(dragged)
        newWgt = None

        if self.getItemType(targetItem) == self.ITEMTYPE_GROUP and self.getItemType(dragged) == self.ITEMTYPE_GROUP \
                and not self.allowSubGroups:
            # Invalid drag events usually has a red crossed circle in PyQt, maybe theres a better way of doing this
            return

        # We have to recreate the componentWidgetItem, because PySide destroys everything on dropEvent.
        # If you do a straight reference change, it crashes. Should look to see if theres a better way
        try:
            newWgt = wgt.copy()
        except AttributeError:
            if wgt is not None:
                print("WARNING: Widget Object doesn't have .copy() function!")
                return

        super(TreeWidget, self).dropEvent(event)

        if newWgt is None:
            return

        newWgt.setParent(self)  # parent must be put here otherwise it will crash

        self.setItemWidget(dragged, self.WIDGET_COL, newWgt)
        self.updateTreeWidget()

    def addNewItem(self, name, widget=None, itemType=ITEMTYPE_WIDGET, icon=None):
        """
        Add a new item type. Should be a group or an itemWidget
        :param addBehaviour:
        :param name:
        :param widget:
        :param itemType:
        :return:
        """

        if itemType == self.ITEMTYPE_WIDGET:
            flags = self.itemWidgetFlags
        else:
            flags = self.groupFlags

        item = self.currentItem()
        treeParent = None

        # If tree parent is left to none it will be added later on to end of the tree by self.addTopLevelItem()
        if item is not None:
            treeParent = self

        newTreeItem = TreeWidgetItem(treeParent, name=name, font=self.font, flags=flags, after=item)
        newTreeItem.setData(self.DATA_COL, QtCore.Qt.EditRole, itemType)  # Data set to column 2, which is not visible
        newTreeItem.setFont(self.WIDGET_COL, self.font)

        if icon is not None:
            newTreeItem.setIcon(self.WIDGET_COL, icon)

        # This will add it in if it wasn't added earlier, if it has then it will just pass through
        self.addTopLevelItem(newTreeItem)

        if widget:
            widget.setParent(self)

        if itemType == self.ITEMTYPE_WIDGET:
            self.updateTreeWidget()
            self.setItemWidget(newTreeItem, self.WIDGET_COL, widget)  # items parent must be set otherwise it will crash

        self.setCurrentItem(newTreeItem)

        return newTreeItem

    def itemWidgets(self, includeNones=False):
        """
        Gets all widgets in the tree. includeNones is for when QTreeWidgetItems don't have a itemWidget attached, but
        for any reason or another we still want to know

        :return: List of itemWidgets
        """
        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(self)
        widgets = []
        for it in treeItemIterator:
            treeItem = it.value()
            if treeItem is not None:
                itemWidget = self.itemWidget(treeItem)
                if itemWidget is None and not includeNones:
                    continue
                widgets.append(self.itemWidget(treeItem))

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
        wgt = self.itemWidget(treeItem)

        if itemType == self.ITEMTYPE_WIDGET:
            # If its an ItemWidget class
            if isinstance(wgt, ItemWidget):
                return wgt.text()

            # Try .name, if all else fails use the text in the widget column
            try:
                return wgt.name
            except AttributeError:
                # If no name is found, just use the treeItem text (the text hidden behind the widget)
                return treeItem.text(self.WIDGET_COL)
        elif itemType == self.ITEMTYPE_GROUP:
            return treeItem.text(self.WIDGET_COL)

    def filter(self, text):
        """
        Hide anything that that doesnt have text. Used for searches.

        :param text:
        :param item:
        :return:
        """

        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(self)

        for it in treeItemIterator:
            treeItem = it.value()
            name = self.getItemName(treeItem)
            
            found = (text in name.lower())
            self.setItemHidden(treeItem, not found)

    def addGroup(self, name="", expanded=True, groupSelected=True):
        """
        Adds a group to the ComponentTreeWidget. If no name is given, it will generate a unique one
        in the form of "Group 1", "Group 2", "Group 3" etc

        TODO: This area still needs a bit of work. Update with addNewItem code
        :param groupSelected:
        :param expanded:
        :param name:
        :return:
        """

        if self.locked:
            print("Locked. Adding of groups disabled")
            return

        # Place group after last selected item
        if len(self.selectedItems()) > 0:
            index = self.indexFromItem(self.selectedItems()[-1]).row() + 1
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
        return self.defaultGroupName + " " + str(num + 1)

    def applyFlags(self):
        """
        Apply flags as set by self.groupFlags and self.componentFlags
        :return:
        """

        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(self)

        for it in treeItemIterator:
            treeItem = it.value()
            if self.getItemType(treeItem) == self.ITEMTYPE_WIDGET:
                treeItem.setFlags(self.itemWidgetFlags)
            elif self.getItemType(treeItem) == self.ITEMTYPE_GROUP:
                treeItem.setFlags(self.groupFlags)


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, name, font, flags, after):
        super(TreeWidgetItem, self).__init__(parent, after)
        self.setText(TreeWidget.WIDGET_COL, name)
        self.setFont(1, font)
        self.setFlags(flags)


class ItemWidget(QtWidgets.QLabel):
    """

    """
    triggered = QtCore.Signal()

    def __init__(self, name):
        super(ItemWidget, self).__init__(name)

        self.emitTarget = None
        self.initUi()

    def initUi(self):
        pass


    def connectEvent(self, func):
        self.emitTarget = func
        self.triggered.connect(func)
        # self.clicked.connect(func)

    def copy(self):
        CurrentType = type(self)
        ret = CurrentType(self.text())
        ret.data = self.data
        # ret.setIcon(self.icon())
        ret.setStyleSheet(self.styleSheet())
        tooltips.copyExpandedTooltips(self, ret)

        return ret

    def mouseDoubleClickEvent(self, event):
        self.triggered.emit()
        # self.emitTarget()
        
    def text(self):
        return super(ItemWidget, self).text()




def copyWidget(w):
    """
    A very shallow copy of the widget. Used more as a placeholder
    :return:
    :rtype: ComponentWidget
    """
    CurrentType = type(w)
    ret = CurrentType()

    try:
        ret.setText(w.text())
    except:
        pass

    try:
        ret.setIcon(w.icon())
    except:
        pass

    try:
        ret.setStyleSheet(w.styleSheet())
    except:
        pass

    return ret
