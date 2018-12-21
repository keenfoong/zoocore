from qt import QtCore, QtWidgets

from zoo.libs import iconlib
from zoo.libs.pyqt import uiconstants, utils
from zoo.libs.pyqt.extended import expandedtooltip
from zoo.libs.pyqt.extended.stackwidget import LineClickEdit
from zoo.libs.pyqt.widgets import frame
from zoo.libs.utils import zlogging
import time

logger = zlogging.getLogger(__name__)


class GroupedTreeWidget(QtWidgets.QTreeWidget):
    ITEMTYPE_WIDGET = "WIDGET"
    ITEMTYPE_GROUP = "GROUP"

    WIDGET_COL = 0
    DATA_COL = 2

    INSERT_AFTERSELECTION = 0
    INSERT_END = 1
    INSERT_ATINDEX = 2

    def __init__(self, parent=None, locked=False, allowSubGroups=True):
        """ A tree widget that has grouping capabilities

        :param parent:
        :param locked:
        :param allowSubGroups:
        """
        super(GroupedTreeWidget, self).__init__(parent)

        self.defaultGroupName = "Group"
        self.setRootIsDecorated(False)

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
        self.connections()

    def initUi(self):
        """ Init Ui Setup

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
        self.setIndentation(10)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def setLocked(self, locked):
        """Sets the lock for drag and drop.

        :param locked:
        :type locked: bool
        """
        self.locked = locked

        if locked:
            self.groupFlags = self.groupFlags & ~self.groupUnlockedFlags
            self.itemWidgetFlags = self.itemWidgetFlags & ~self.itemWidgetUnlockedFlags
        else:
            self.groupFlags = self.groupFlags | self.groupUnlockedFlags
            self.itemWidgetFlags = self.itemWidgetFlags | self.itemWidgetUnlockedFlags

        self.applyFlags()

    def connections(self):
        self.itemSelectionChanged.connect(self.treeSelectionChanged)

    def treeSelectionChanged(self):
        pass

    def initDragDrop(self):
        """ Set up Drag drop Settings for this widget
        """

        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(
            QtCore.Qt.CopyAction)  # For some reason dropMimeData doesn't get called if its set to Qt.MoveAction
        self.setAcceptDrops(True)

    def supportedDropActions(self):
        """Supported actions of the drag drop
        """
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction

    def dropMimeData(self, parent, index, data, action):
        """ Dropping data from one spot to another.

        :param parent:
        :param index:
        :param data:
        :param action:
        :return:
        :todo: Wip

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

    def mimeTypes(self):
        """Mimetypes that are allowed in the drag drop

        :return:
        :todo: WIP
        """
        return ['text/xml']

    def mimeData(self, items):
        """The data that will be dragged between tree nodes

        :param items: List of selected TreeWidgetItems
        :type items: list(TreeWidgetItem)
        :return:
        """

        self.dragWidgets = []
        for item in items:
            itemWidget = self.itemWidget(item)
            self.dragWidgets.append(
                {'itemWidget': itemWidget, 'icon': item.icon(0), 'itemType': self.getItemType(item)})

        self.removeForDrop = items

        mimedata = super(GroupedTreeWidget, self).mimeData(items)

        return mimedata

    def setCurrentItems(self, items):
        """Selects the items in the TreeWidget

        :param items:
        """
        prevMode = self.selectionMode()
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        for item in items:
            self.setCurrentItem(item)
        self.setSelectionMode(prevMode)

    def removeDropItems(self):
        """ Remove the source items from the treewidget that has been dragged

        :return:
        """
        for r in self.removeForDrop:
            (r.parent() or self.invisibleRootItem()).removeChild(r)

    def insertNewItem(self, name, widget=None, index=0, treeParent=None, itemType=ITEMTYPE_WIDGET, icon=None):
        """ Inserts a new item at a location, and sets the widget as the itemWidget

        ItemType can be Widget or Group. Groups wont have user customized widgets, but can have children.
        ITEMTYPE_WIDGETS wont have children.

        May merge with self.addNewItem()

        :param name: Name of the new Item, generally put into the text field of the TreeWidgetItem. This is the text \
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

        newTreeItem = TreeWidgetItem(None, name=name, flags=flags)
        newTreeItem.setData(self.DATA_COL, QtCore.Qt.EditRole, itemType)  # Data set to column 2, which is not visible
        if icon is not None:
            newTreeItem.setIcon(self.WIDGET_COL, icon)

        (treeParent or self.invisibleRootItem()).insertChild(index, newTreeItem)
        if widget is not None:
            widget.setParent(self)
            self.setItemWidget(newTreeItem, self.WIDGET_COL, widget)
            if hasattr(widget, "toggleExpandRequested"):
                widget.toggleExpandRequested.connect(self.updateTreeWidget)
                widget.toggleExpandRequested.connect(newTreeItem.setExpanded)
            self.updateTreeWidget()

        return newTreeItem

    def addNewItem(self, name, widget=None, itemType=ITEMTYPE_WIDGET, icon=None):
        """Add a new item type. Should be a group or an itemWidget. If you'd like to add a TreeWidgetItem instead, use
        addNewTreeWidgetItem()

        ItemType can be Widget or Group. Groups wont have user customized widgets, but can have children.
        ITEMTYPE_WIDGETS wont have children.

        May merge with self.insertNewItem()

        :param name: Name of the new Item, generally put into the text field of the TreeWidgetItem. This is the text \
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

        newTreeItem = TreeWidgetItem(treeParent, name=name, flags=flags, after=item)
        newTreeItem.setData(self.DATA_COL, QtCore.Qt.EditRole, itemType)  # Data set to column 2, which is not visible

        if icon is not None:
            newTreeItem.setIcon(self.WIDGET_COL, icon)

        # This will add it in if it wasn't added earlier, if it has then it will just pass through
        self.addTopLevelItem(newTreeItem)

        if widget:

            widget.setParent(self)
            if self.updatesEnabled():
                self.updateTreeWidget()

            self.setItemWidget(newTreeItem, self.WIDGET_COL, widget)  # items parent must be set otherwise it will crash
            # temp hack to support rowheight refresh, need to replace
            if hasattr(widget, "toggleExpandRequested"):
                widget.toggleExpandRequested.connect(self.updateTreeWidget)
                widget.toggleExpandRequested.connect(newTreeItem.setExpanded)
        self.setCurrentItem(newTreeItem)

        return newTreeItem

    def itemWidgets(self, itemType=None, treeItem=None):
        """Gets all widgets in the tree. includeNones is for when QTreeWidgetItems don't have a itemWidget attached, but
        for any reason or another we still want to know

        :return: List of itemWidgets
        """
        if treeItem is not None:
            iteratorItem = treeItem
        else:
            iteratorItem = self
        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(iteratorItem)
        widgets = []
        for it in treeItemIterator:
            treeItem = it.value()
            if treeItem is not None:
                itemWidget = self.itemWidget(treeItem)
                if itemWidget is None:
                    continue

                # Add by type, but if itemType is none, let them all through
                if (itemType is not None and self.getItemType(treeItem) == itemType) or \
                        itemType is None:
                    widgets.append(itemWidget)

        return widgets

    def treeWidgetItemByHash(self, treeItemHash):
        """Return TreeWidgetItem by hash.
        If this is slow maybe we should put all the treeWidgetItems in a hash map as well.

        :param treeItemHash:
        :return:
        :rtype: TreeWidgetItem or None
        """
        if treeItemHash is None:
            return

        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(self)

        for it in treeItemIterator:
            treeItem = it.value()
            if hash(treeItem) == treeItemHash:
                return treeItem

    def itemWidget(self, treeItem, col=None):
        """Short hand to get the item widget from the default column (as defined by self.WIDGET_COL)

        :param treeItem:
        :param col:
        :return:
        """
        col = col or self.WIDGET_COL

        return super(GroupedTreeWidget, self).itemWidget(treeItem, col)

    def updateTreeWidget(self):
        """ Updates the tree widget so the row heights of the TreeWidgetItems matches what the ComponentWidgets ask for
        in terms of the sizeHint() asks for
        """
        # Super hacky way to update the TreeWidget, add an empty object and then remove it
        self.insertTopLevelItem(0, QtWidgets.QTreeWidgetItem())
        self.takeTopLevelItem(0)

    def getItemType(self, treeItem):
        """ Get the item type ("COMPONENT" or "GROUP")

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
            if isinstance(wgt, ItemWidgetLabel):
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
        """ Hide anything that that doesnt have text. Used for searches.

        :param text:
        """

        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(self)

        for it in treeItemIterator:
            treeItem = it.value()
            name = self.getItemName(treeItem)

            found = (text in name.lower())
            self.setItemHidden(treeItem, not found)

    def addGroup(self, name="", expanded=True, groupSelected=True, groupWgt=None):
        """ Adds a group to the ComponentTreeWidget. If no name is given, it will generate a unique one
        in the form of "Group 1", "Group 2", "Group 3" etc

        :param groupSelected:
        :param expanded:
        :param name:
        :param groupWgt: Use this as the widget, if its none we'll just use the text background as the display
        :return:
        :todo: This area still needs a bit of work. Update with addNewItem code
        """

        if self.locked:
            logger.warning("Locked. Adding of groups disabled")
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

                self.addToGroup(s, group)

        group.setExpanded(expanded)
        self.updateTreeWidget()

        groupWgt.setTreeItem(group)

        return group

    def insertGroup(self, name="", index=0, treeParent=None, expanded=True, groupWgt=None, icon=None):
        """Inserts a group into index, underneath treeParent.

        :param name:
        :param index:
        :param treeParent:
        :param expanded:
        :param groupWgt:
        :type groupWgt: zoo.apps.hiveartistui.views.componentwidget.ComponentGroupWidget
        :param icon:
        :return:
        """
        if self.locked:
            logger.warning("Locked. Adding of groups disabled")
            return

        name = name or self.getUniqueGroupName()
        group = self.insertNewItem(name, widget=groupWgt, index=index, treeParent=treeParent,
                                   itemType=self.ITEMTYPE_GROUP, icon=icon)

        groupWgt.setTreeItem(group)

    def addToGroup(self, item, group):
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

        if self.updatesEnabled():
            self.updateTreeWidget()

    def getUniqueGroupName(self):
        """Returns a unique group name: "Group 1", "Group 2", "Group 3" etc.

        :return:
        :rtype: str
        """
        num = len(self.findItems(self.defaultGroupName + " *", QtCore.Qt.MatchFlag.MatchWildcard, 0))
        return self.defaultGroupName + " " + str(num + 1)

    def applyFlags(self):
        """ Apply flags as set by self.groupFlags and self.itemWidgetFlags.

        ITEMTYPE_WIDGET gets applied a different set of drag drop flags to
        ITEMWIDGET_GROUP
        """
        treeItemIterator = QtWidgets.QTreeWidgetItemIterator(self)
        for it in treeItemIterator:
            treeItem = it.value()
            if self.getItemType(treeItem) == self.ITEMTYPE_WIDGET:
                treeItem.setFlags(self.itemWidgetFlags)
            elif self.getItemType(treeItem) == self.ITEMTYPE_GROUP:
                treeItem.setFlags(self.groupFlags)

    def iterator(self):
        """
        Iterator to iterate through the treeItems

        .. code-block:: python

            for it in treeItemIterator:
                treeItem = it.value()

        """
        return QtWidgets.QTreeWidgetItemIterator(self)


class GroupWidget(QtWidgets.QWidget):
    """
    The Widget used for groups in TreeWidget
    """
    _deleteIcon = iconlib.icon("xMark")
    _itemIcon = iconlib.icon("openFolder01")
    _collapsedIcon = iconlib.icon("sortClosed")
    _expandIcon = iconlib.icon("sortDown")

    def __init__(self, title="", parent=None, treeItem=None):
        super(GroupWidget, self).__init__(parent=parent)

        self.color = uiconstants.DARKBGCOLOR
        self.horizontalLayout = utils.hBoxLayout(self)
        self.mainLayout = utils.hBoxLayout(self)
        self.expandToggleButton = QtWidgets.QToolButton(parent=self)
        self.folderIcon = QtWidgets.QToolButton(parent=self)
        self.titleFrame = frame.QFrame(parent=self)
        self.collapsed = False

        self.groupTextEdit = LineClickEdit(title, single=False)
        self.titleExtrasLayout = QtWidgets.QHBoxLayout()
        self.deleteBtn = QtWidgets.QToolButton(parent=self)
        self.treeItem = treeItem

        self.initUi()
        self.connections()

    def initUi(self):
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.folderIcon.setIcon(self._itemIcon)
        self.deleteBtn.setIcon(self._deleteIcon)

        self.buildTitleFrame()

    def setTreeItem(self, treeItem):
        self.treeItem = treeItem

    def connections(self):
        self.expandToggleButton.clicked.connect(self.expandToggle)

    def text(self):
        """
        Returns the text of the text edit
        :return:
        """
        return self.groupTextEdit.text()

    def buildTitleFrame(self):
        """Builds the title part of the layout with a QFrame widget
        """

        self.layout().addWidget(self.titleFrame)

        self.titleFrame.setContentsMargins(1, 1, 4, 0)
        self.titleFrame.mousePressEvent = self.mousePressEvent

        # the horizontal layout
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.titleFrame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # the icon and title and spacer
        self.expandToggleButton.setParent(self.titleFrame)
        if self.collapsed:
            self.expandToggleButton.setIcon(self._collapsedIcon)
        else:
            self.expandToggleButton.setIcon(self._expandIcon)

        self.folderIcon.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        spacerItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # add to horizontal layout
        self.horizontalLayout.addWidget(self.expandToggleButton)
        self.horizontalLayout.addWidget(self.folderIcon)
        self.horizontalLayout.addItem(spacerItem)
        self.titleFrame.setFixedHeight(self.titleFrame.sizeHint().height())

        self.setMinimumSize(self.titleFrame.sizeHint().width(), self.titleFrame.sizeHint().height()+3)

        self.horizontalLayout.addWidget(self.groupTextEdit)
        self.horizontalLayout.addLayout(self.titleExtrasLayout)
        self.horizontalLayout.addWidget(self.deleteBtn)

        self.horizontalLayout.setStretchFactor(self.groupTextEdit, 4)

    def expandToggle(self):
        if self.collapsed:
            self.expand()
            self.collapsed = False
        else:
            self.collapse()
            self.collapsed = True

    def onCollapsed(self):
        """
        Collapse and hide the item contents
        :return:
        """
        self.expandToggleButton.setIcon(self._collapsedIcon)
        self.treeItem.setExpanded(False)

    def onExpand(self):
        self.expandToggleButton.setIcon(self._expandIcon)
        self.treeItem.setExpanded(True)

    def expand(self):
        """ Extra Code for convenience """
        self.onExpand()

    def collapse(self):
        """ Extra Code for convenience """
        self.onCollapsed()

    def mousePressEvent(self, event):
        event.ignore()

    def passThroughMouseEvent(self, event):
        event.ignore()


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, name, flags, after=None):
        super(TreeWidgetItem, self).__init__(parent, after)
        self.setText(GroupedTreeWidget.WIDGET_COL, name)

        self.setFlags(flags)


class ItemWidgetLabel(QtWidgets.QLabel):
    """

    """
    triggered = QtCore.Signal()

    def __init__(self, name):
        super(ItemWidgetLabel, self).__init__(name)

        self.emitTarget = None
        self.initUi()

    def initUi(self):
        pass

    def connectEvent(self, func):
        self.emitTarget = func
        self.triggered.connect(func)

    def copy(self):
        CurrentType = type(self)
        ret = CurrentType(self.text())
        ret.name = self.name
        # ret.setIcon(self.icon())
        ret.setStyleSheet(self.styleSheet())
        expandedtooltip.copyExpandedTooltips(self, ret)

        return ret

    def mouseDoubleClickEvent(self, event):
        self.triggered.emit()
        # self.emitTarget()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()

    def text(self):
        return super(ItemWidgetLabel, self).text()
