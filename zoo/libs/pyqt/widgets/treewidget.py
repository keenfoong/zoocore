import cPickle
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
        """
        Updates the TreeWidget UI for QT sizehints and visuals
        :return:
        """
        if self.treeWidget is not None:
            self.treeWidget.updateTreeWidget()


class TreeWidget(QtWidgets.QTreeWidget):
    """
    A custom tree widget with some default settings we want in our zoo UI
    """

    ITEMTYPE_WIDGET = "WIDGET"
    ITEMTYPE_GROUP = "GROUP"

    WIDGET_COL = 0
    DATA_COL = 2

    INSERT_AFTERSELECTION = 0
    INSERT_END = 1
    INSERT_ATINDEX = 2

    def __init__(self, parent=None, locked=False, allowSubGroups=True):
        super(TreeWidget, self).__init__(parent)

        self.defaultGroupName = "Group"

        self.font = QtGui.QFont("sans")

        # Drag drop
        self.removeForDrop = []  # type: list(TreeWidgetItem)
        self.dragWidgets = []

        # Grouping flags
        self.allowSubGroups = allowSubGroups
        self.headerItem = None  # type: QtWidgets.QTreeWidgetItem

        self.groupFlags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        self.groupUnlockedFlags = QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

        self.itemWidgetFlags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled
        self.itemWidgetUnlockedFlags = QtCore.Qt.ItemIsDragEnabled

        self.locked = locked
        self.setLocked(locked)

        self.initUi()

    def setLocked(self, locked):
        """
        Sets the lock for drag and drop.
        :param locked:
        :type locked: bool
        :return:
        """
        self.locked = locked

        if locked:
            self.groupFlags = self.groupFlags & ~self.groupUnlockedFlags
            self.itemWidgetFlags = self.itemWidgetFlags & ~self.itemWidgetUnlockedFlags
        else:
            self.groupFlags = self.groupFlags | self.groupUnlockedFlags
            self.itemWidgetFlags = self.itemWidgetFlags | self.itemWidgetUnlockedFlags

        self.applyFlags()

    def initUi(self):
        """
        Init Ui Setup
        :return:
        """
        # Header setup
        self.headerItem = QtWidgets.QTreeWidgetItem(["Widget"])
        self.setHeaderItem(self.headerItem)
        self.header().hide()

        self.initDragDrop()

        self.resizeColumnToContents(1)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setIndentation(mayaui.dpiScale(10))
        self.setFocusPolicy(QtCore.Qt.NoFocus)


    def initDragDrop(self):
        """
        Set up Drag drop Settings for this widget
        :return:
        """
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.CopyAction) # For some reason dropMimeData doesn't get called if its set to Qt.MoveAction
        self.setAcceptDrops(True)

    def supportedDropActions(self):
        """
        Supported actions of the drag drop
        :return:
        """
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction

    def dropMimeData(self, parent, index, data, action):
        """
        Dropping data from one spot to another.
        TODO: Wip
        :param parent:
        :param index:
        :param data:
        :param action:
        :return:
        """
        group = parent or self.invisibleRootItem()
        newItems = []
        for g in reversed(self.dragWidgets):
            newTreeItem = self.insertNewItem("", g['itemWidget'], index, group,
                                             itemType=g['itemType'], icon=g['icon'])
            newItems.append(newTreeItem)

        self.removeDropItems()
        self.setCurrentItems(newItems)
        return True

    def setCurrentItems(self, items):
        """
        Selects the items in the TreeWidget
        :param items:
        :return:
        """
        prevMode = self.selectionMode()
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        for item in items:
            self.setCurrentItem(item)
        self.setSelectionMode(prevMode)

    def mimeTypes(self):
        """
        Mimetypes that are allowed in the drag drop
        TODO: WIP
        :return:
        """
        return ['text/xml']

    def mimeData(self, items):
        """
        The data that will be dragged between tree nodes

        :param items: List of selected TreeWidgetItems
        :type items: list(TreeWidgetItem)

        :return:
        """

        self.dragWidgets = []
        for item in items:
            itemWidget = self.itemWidget(item)
            self.dragWidgets.append({'itemWidget': itemWidget, 'icon': item.icon(0), 'itemType':self.getItemType(item)})

        self.removeForDrop = items

        mimedata = super(TreeWidget, self).mimeData(items)

        return mimedata

    def removeDropItems(self):
        """
        Remove the source items from the treewidget that has been dragged
        :return:
        """
        for r in self.removeForDrop:
            (r.parent() or self.invisibleRootItem()).removeChild(r)

    def insertNewItem(self, name, widget=None, index=0, treeParent=None, itemType=ITEMTYPE_WIDGET, icon=None):
        """
        Inserts a new item at a location, and sets the widget as the itemWidget.
        ItemType can be Widget or Group. Groups wont have user customized widgets, but can have children.
        ITEMTYPE_WIDGETS wont have children.

        May merge with self.addNewItem()
        :param name: Name of the new Item, generally put into the text field of the TreeWidgetItem. This is the text
                     that is used for the search bar if it is active.

        :param widget: Expects ItemWidget or any subclass of QtWidgets.QWidget.
        :param index: Index to insert into
        :param treeParent: The parent that it will insert into. If treeParent is None, it will assume the parent to be Root
        :type treeParent: TreeWidgetItem or None
        :param itemType: The type of widget being set for the new Item.
        :param icon: Icon to set for the TreeWidgetItem
        :return: The new item created
        :rtype: TreeWidgetItem
        """
        if itemType == self.ITEMTYPE_WIDGET:
            flags = self.itemWidgetFlags
        else:
            flags = self.groupFlags

        newTreeItem = TreeWidgetItem(None, name=name, font=self.font, flags=flags)
        newTreeItem.setData(self.DATA_COL, QtCore.Qt.EditRole, itemType)  # Data set to column 2, which is not visible
        if icon is not None:
            newTreeItem.setIcon(self.WIDGET_COL, icon)
        newTreeItem.setFont(self.WIDGET_COL, self.font)

        (treeParent or self.invisibleRootItem()).insertChild(index, newTreeItem)

        self.updateTreeWidget()
        widget.setParent(self)
        self.setItemWidget(newTreeItem, self.WIDGET_COL, widget)

        return newTreeItem

    def addNewItem(self, name, widget=None, itemType=ITEMTYPE_WIDGET, icon=None):
        """
        Add a new item type. Should be a group or an itemWidget

        ItemType can be Widget or Group. Groups wont have user customized widgets, but can have children.
        ITEMTYPE_WIDGETS wont have children.

        May merge with self.insertNewItem()

        :param name: Name of the new Item, generally put into the text field of the TreeWidgetItem. This is the text
                     that is used for the search bar if it is active.
        :param widget: Expects ItemWidget or any subclass of QtWidgets.QWidget.
        :param itemType: The type of widget being set for the new Item.
        :param icon: Icon to set for the TreeWidgetItem
        :return: The new item created
        :rtype: TreeWidgetItem
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

            self.updateTreeWidget()
            self.setItemWidget(newTreeItem, self.WIDGET_COL, widget)  # items parent must be set otherwise it will crash

        self.setCurrentItem(newTreeItem)

        return newTreeItem

    def itemWidgets(self, includeNones=False, itemType=None):
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

                # Add by type
                if itemType is not None and self.getItemType(treeItem) == itemType:
                    widgets.append(self.itemWidget(treeItem))

        return widgets

    def treeWidgetItemByHash(self, treeItemHash):
        """
        Return TreeWidgetItem by hash.
        If this is slow maybe we should put all the treeWidgetItems in a hash map as well.
        :param treeItemHash:
        :return:
        :rtype: TreeWidgetItem
        """
        if treeItemHash is None:
            return None

        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(self)

        for it in treeItemIterator:
            treeItem = it.value()
            if hash(treeItem) == treeItemHash:
                return treeItem

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
        self.takeTopLevelItem(0)

    def getItemType(self, treeItem):
        """
        Get the item type ("COMPONENT" or "GROUP")

        :param treeItem: The TreeWidgetItem to get the type of
        :type treeItem: TreeWidgetItem
        :return:
        """
        print(treeItem)
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
        :return:
        """

        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(self)

        for it in treeItemIterator:
            treeItem = it.value()
            name = self.getItemName(treeItem)

            found = (text in name.lower())
            self.setItemHidden(treeItem, not found)

    def addGroup(self, name="", expanded=True, groupSelected=True, groupWgt=None):
        """
        Adds a group to the ComponentTreeWidget. If no name is given, it will generate a unique one
        in the form of "Group 1", "Group 2", "Group 3" etc

        TODO: This area still needs a bit of work. Update with addNewItem code
        :param groupSelected:
        :param expanded:
        :param name:
        :param groupWgt: Use this as the widget, if its none we'll just use the text background as the display
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
        group = self.addNewItem(name, groupWgt, self.ITEMTYPE_GROUP)
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

    def insertGroup(self, name="", index=0, treeParent=None, expanded=True, groupWgt=None, icon=None):
        """
        Inserts a group into index, underneath treeParent.
        :param name:
        :param index:
        :param treeParent:
        :param expanded:
        :param groupWgt:
        :param icon:
        :return:
        """
        if self.locked:
            print("Locked. Adding of groups disabled")
            return

        name = name or self.getUniqueGroupName()
        group = self.insertNewItem(name, widget=groupWgt, index=index, treeParent=treeParent,
                                   itemType=self.ITEMTYPE_GROUP, icon=icon)
        #group.setExpanded(expanded)

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
        Apply flags as set by self.groupFlags and self.itemWidgetFlags.
        ITEMTYPE_WIDGET gets applied a different set of drag drop flags to
        ITEMWIDGET_GROUP
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
    def __init__(self, parent, name, font, flags, after=None):
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
        ret.name = self.name
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
