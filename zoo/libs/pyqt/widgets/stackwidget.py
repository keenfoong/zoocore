
from qt import QtWidgets, QtCore, QtGui
from zoo.libs import iconlib
from zoo.libs.pyqt.widgets import layouts
from zoo.libs.pyqt import uiconstants
from zoo.libs.pyqt.widgets import frame



class StackWidget(QtWidgets.QWidget):
    """
    The overall layout widget. The table underneath (self.stackTableWgt) holds all the stack items.
    TODO: StackItem has been changed to use QSignals for ShiftUp, shiftDown, updateSize, delete. This needs to reflect that
    """
    _expandIcon = iconlib.icon("roundedsquare")
    _collapseIcon = iconlib.icon("minus")

    def __init__(self, label="", parent=None, showToolbar=True, showArrows=True, showClose=True, titleEditable=True):
        super(StackWidget, self).__init__(parent=parent)

        self.stackTableWgt = StackTableWidget(showArrows=showArrows, showClose=showClose, parent=self)
        self.stackItems = self.stackTableWgt.stackItems
        self.stackSearchEdit = QtWidgets.QLineEdit(parent=self)
        self.collapseBtn = QtWidgets.QPushButton(parent=self)
        self.expandBtn = QtWidgets.QPushButton(parent=self)

        self.text = label
        self.showToolbar = showToolbar
        self.showArrows = showArrows
        self.showClose = showClose
        self.titleEditable = titleEditable

        self.initUi()

        self.connections()

    def __len__(self):
        return len(self.stackItems)

    def __iter__(self):
        for i in self.stackItems:
            yield i

    def initUi(self):

        compStackToolbarLayout = QtWidgets.QHBoxLayout()
        compStackToolbarLayout.addWidget(self.stackSearchEdit)

        self.expandBtn.setIcon(self._expandIcon)
        self.expandBtn.setIconSize(QtCore.QSize(12, 12))

        self.collapseBtn.setIcon(self._collapseIcon)
        self.collapseBtn.setIconSize(QtCore.QSize(10, 10))

        size = QtCore.QSize(self.collapseBtn.sizeHint().width(), 20)  # Temporary size till we get icons here
        self.collapseBtn.setFixedSize(size)
        self.expandBtn.setFixedSize(size)

        compStackToolbarLayout.addSpacing(5)
        compStackToolbarLayout.addWidget(self.collapseBtn)
        compStackToolbarLayout.addWidget(self.expandBtn)

        compStackToolbarLayout.setStretchFactor(self.stackSearchEdit, 1)

        compStackToolbarLayout.setContentsMargins(0, 0, 0, 0)
        compStackToolbarLayout.setSpacing(2)

        compStackToolbar = QtWidgets.QWidget(parent=self)
        compStackToolbar.setLayout(compStackToolbarLayout)

        mainLayout = QtWidgets.QVBoxLayout()

        if self.text != "":
            mainLayout.addWidget(QtWidgets.QLabel(self.text))

        if not self.showToolbar:
            compStackToolbar.hide()

        mainLayout.addWidget(compStackToolbar)
        mainLayout.addWidget(self.stackTableWgt)

        self.setLayout(mainLayout)

    def connections(self):
        self.stackSearchEdit.textChanged.connect(self.onStackSearchChanged)

        self.collapseBtn.clicked.connect(self.collapseClicked)
        self.expandBtn.clicked.connect(self.expandClicked)

    def collapseClicked(self):
        self.stackTableWgt.collapseAll()

    def expandClicked(self):
        self.stackTableWgt.expandAll()

    def onStackSearchChanged(self):

        text = self.stackSearchEdit.text().lower()
        self.stackTableWgt.filter(text)
        self.stackTableWgt.updateSize()

    def clearStack(self):
        self.stackTableWgt.clearStack()

    def addStackItem(self, item):
        item.setArrowsVisible(self.showArrows)
        self.stackTableWgt.addStackItem(item)

    def replaceStackItems(self, items):
        self.clearStack()
        for i in items:
            self.stackTableWgt.addStackItem(i)

    def clearSearchEdit(self):
        self.stackSearchEdit.setText("")

    def shiftItem(self, wgt, dir):
        self.stackTableWgt.shiftTableItem(wgt, dir)

    def deleteItem(self, wgt):
        self.stackTableWgt.deleteTableItem(wgt)


class StackTableWidget(QtWidgets.QTableWidget):
    """
    The Table with the actual stack and items. Maybe should merge with StackWidget
    """

    def __init__(self, showArrows=True, showClose=True, parent=None, itemTint=tuple([60,60,60])):
        super(StackTableWidget, self).__init__(parent)
        self.cellPadding = 5
        self.stackItems = []
        self.showArrows = showArrows
        self.showClose = showClose
        self.itemTint = itemTint
        style = """
            QTableView {{
            background-color: rgb{0};
            border-size: 0px;
            }}

            QTableView:item {{
            padding:{1}px;
            border-size: 0px;
            }}
            """.format(str(uiconstants.MAYABGCOLOR), self.cellPadding)
        self.setShowGrid(False)
        self.initUi()

        self.setStyleSheet(style)


    def initUi(self):
        self.setRowCount(0)
        self.setColumnCount(1)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        self.horizontalHeader().setStretchLastSection(True)

        self.setContentsMargins(2, 2, 2, 2)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)


    def contextMenu(self, pos):
        #print('column(%d)' % self.table.horizontalHeader().logicalIndexAt(pos))
        print ("Context menu")
        """
        selectionModel = self.selectionModel()
        selection = [model.itemFromIndex(index) for index in selectionModel.selectedIndexes()]
        """

        menu = QtWidgets.QMenu()
        menu.addAction('Component Settings')
        menu.addSeparator()
        menu.addAction('Group')
        menu.addSeparator()
        menu.addAction('Cut')
        menu.addAction('Copy')
        menu.addAction('Paste')
        menu.exec_(QtGui.QCursor.pos())

    def shiftTableItem(self, wgt, dir):
        # Update componentList
        # self.shiftComponentStack(wgt, dir)

        row = self.getRow(wgt)

        if row == 0 and dir == -1 or row == self.rowCount() - 1 and dir == 1:
            return

        # newRow = row + dir
        # Have to do this in a funky way because removeRow deletes the object
        # and swapping cells gives weird results
        if dir > 0:  # Even then this is ugly lol, need to fix
            newRow = row + dir + 1
            remRow = row
        else:
            newRow = row + dir
            remRow = row + 1

        self.insertRow(newRow)
        self.setCellWidget(newRow, 0, wgt)
        self.removeRow(remRow)
        self.updateSize(wgt)

    def collapseAll(self):
        for c in self.stackItems:
            c.collapse()

    def expandAll(self):
        for c in self.stackItems:
            c.expand()

    def deleteTableItem(self, wgt):

        row = self.getRow(wgt)
        self.removeRow(row)
        self.stackItems.remove(wgt)

        wgt.deleteLater()

    def addStackItem(self, item):

        self.stackItems.append(item)
        self.addRow(item)

        self.updateSize(item)
        #item.show()

    def addRow(self, stackItem):
        rowPos = self.rowCount()
        self.setRowCount(rowPos + 1)
        self.setItem(rowPos, 0, QtWidgets.QTableWidgetItem())
        self.setCellWidget(rowPos, 0, stackItem)

        #self.updateSize(stackItem)

        #self.setRowHeight(rowPos, stackItem.sizeHint().height())

    def getRow(self, stackItem):
        for i in range(self.rowCount()):
            if stackItem == self.cellWidget(i, 0):
                return i

    def filter(self, text):
        for i in range(self.rowCount()):
            found = not (text in self.cellWidget(i, 0).getTitle().lower())
            self.setRowHidden(i, found)

    def getStackItems(self):
        return self.stackItems

    def updateSize(self, widget=None):
        """
        Updates the size based on the widget who sent the request.
        Can be forced by setting the widget parameter
        :param widget:
        :return:
        """

        if widget is not None:
            print("widget not none")
            stackItem = widget
        else:
            print("widget none")
            stackItem = self.sender()

            if stackItem is None:
                return

        # So ugly =( This is is so the sizeHint refreshes properly otherwise the StackItem will be stuck at zero height
        QtWidgets.QApplication.processEvents()  # this must be here otherwise the resize is calculated too quickly

        newHeight = stackItem.sizeHint().height() + self.cellPadding * 2

        self.setRowHeight(self.getRow(stackItem), newHeight)


    def clearStack(self):
        self.stackItems = []
        self.clear()
        self.setRowCount(0)

    def sceneRefresh(self):
        self.clearStack()


class StackItem(QtWidgets.QWidget):
    """
    The item in each StackTableWidget.
    Modified version of CollapsableFrameLayout in layouts.py
    """
    _downIcon = iconlib.icon("arrowSingleDown")
    _upIcon = iconlib.icon("arrowSingleUp")
    _deleteIcon = iconlib.icon("xMark")
    _itemIcon = iconlib.icon("stream")

    closeRequested = QtCore.Signal()
    openRequested = QtCore.Signal()
    shiftUpPressed = QtCore.Signal()
    shiftDownPressed = QtCore.Signal()
    deletePressed = QtCore.Signal()
    updateRequested = QtCore.Signal()
    
    _collapsedIcon = iconlib.icon("sortClosed")
    _expandIcon = iconlib.icon("sortDown")

    def __init__(self, title, parent, collapsed=False, collapsable=True, icon=None, startHidden=False,
                 itemTint=tuple([60,60,60]), shiftArrowsEnabled=True, deleteButtonEnabled=True):
        super(StackItem, self).__init__(parent=parent)

        if startHidden:
            self.hide()

        self.itemTint = itemTint

        self._itemIcon = icon or self._itemIcon
        self.stackWidget = parent

        # Init
        self.itemIcon = QtWidgets.QToolButton(parent=self)
        self.shiftDownBtn = QtWidgets.QToolButton(parent=self)
        self.shiftUpBtn = QtWidgets.QToolButton(parent=self)
        self.deleteBtn = QtWidgets.QToolButton(parent=self)
        self.stackTitleWgt = QtWidgets.QLineEdit(title)
        self.titleExtrasLayout = QtWidgets.QHBoxLayout()

        self.spacesToUnderscore = True

        ### TODO: From layouts.py. Should be cleaned up
        contentMargins = uiconstants.MARGINS
        contentSpacing = uiconstants.SPACING
        color = uiconstants.DARKBGCOLOR

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.titleExtrasLayout.setContentsMargins(0,0,0,0)
        self.titleExtrasLayout.setSpacing(0)
        self.title = title
        self.color = color
        self.contentMargins = contentMargins
        self.contentSpacing = contentSpacing
        self.collapsable = collapsable
        self.collapsed = collapsed

        if not shiftArrowsEnabled:
            self.shiftDownBtn.hide()
            self.shiftUpBtn.hide()

        if not deleteButtonEnabled:
            self.deleteBtn.hide()

        if hasattr(self.stackWidget, 'showClose') and  not self.stackWidget.showClose:
            self.deleteBtn.hide()

        if hasattr(self.stackWidget, 'titleEditable') and not self.stackWidget.titleEditable:
            self.stackTitleWgt.setReadOnly(True)

        self.initUi()
        self.setLayout(self.layout)

        self.connections()

        if not collapsable:  # if not collapsable must be open
            self.collapsed = False
            self.expand()

        if self.collapsed:
            self.collapse()
        else:
            self.expand()

    def setArrowsVisible(self, visible):
        if visible:
            self.shiftDownBtn.show()
            self.shiftUpBtn.show()
        else:
            self.shiftDownBtn.hide()
            self.shiftUpBtn.hide()


    def initUi(self):

        ### TODO: From Layouts
        self.buildTitleFrame()
        self.buildHiderWidget()
        self.layout.addWidget(self.titleFrame)
        self.layout.addWidget(self.widgetHider)
        ###


        self.itemIcon.setIcon(self._itemIcon)
        self.shiftDownBtn.setIcon(self._downIcon)
        self.shiftUpBtn.setIcon(self._upIcon)
        self.deleteBtn.setIcon(self._deleteIcon)

        self.deleteBtn.setIconSize(QtCore.QSize(12, 12))
        self.shiftUpBtn.setIconSize(QtCore.QSize(12, 12))
        self.shiftDownBtn.setIconSize(QtCore.QSize(12, 12))
        # self.itemIcon.setIconSize(QtCore.QSize(24, 24))

        self.horizontalLayout.insertWidget(1, self.itemIcon)
        self.horizontalLayout.addWidget(self.stackTitleWgt)
        self.horizontalLayout.addLayout(self.titleExtrasLayout)
        self.horizontalLayout.addWidget(self.shiftUpBtn)
        self.horizontalLayout.addWidget(self.shiftDownBtn)
        self.horizontalLayout.addWidget(self.deleteBtn)

        # Possibly should tweak layouts.CollapsableFrameLayout (or create a new class) instead of adding then deleting
        i = self.horizontalLayout.indexOf(self.titleLabel)
        self.horizontalLayout.takeAt(i)
        self.titleLabel.deleteLater()





        self.horizontalLayout.setStretchFactor(self.stackTitleWgt, 4)


    def buildTitleFrame(self):
        """Builds the title part of the layout with a QFrame widget
        """
        #TODO: From layouts
        # main dark grey qframe
        self.titleFrame = frame.QFrame(parent=self)
        self.setFrameColor(self.color)
        self.titleFrame.setContentsMargins(4, 0, 4, 0)

        # the horizontal layout
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.titleFrame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # the icon and title and spacer
        self.iconButton = QtWidgets.QToolButton(parent=self)
        if self.collapsed:
            self.iconButton.setIcon(self._collapsedIcon)
        else:
            self.iconButton.setIcon(self._expandIcon)
        self.titleLabel = QtWidgets.QLabel(self.title, parent=self)
        self.titleLabel.setStyleSheet("font: bold;")
        self.titleLabel.setContentsMargins(0, 0, 0, 0)
        spacerItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # add to horizontal layout
        self.horizontalLayout.addWidget(self.iconButton)
        self.horizontalLayout.addWidget(self.titleLabel)
        self.horizontalLayout.addItem(spacerItem)
        self.titleFrame.setFixedHeight(self.titleFrame.sizeHint().height())
        self.setMinimumSize(self.titleFrame.sizeHint().width(), self.titleFrame.sizeHint().height())

    def shiftUp(self):
        #self.stackWidget.shiftItem(self, -1)
        self.shiftUpPressed.emit()


    def shiftDown(self):
        #self.stackWidget.shiftItem(self, 1)
        self.shiftDownPressed.emit()

    def addWidget(self, widget):
        self.hiderLayout.addWidget(widget)

    def addLayout(self, layout):
        self.hiderLayout.addLayout(layout)

    def buildHiderWidget(self):
        """Builds widget that is collapsable
        Widget can be toggled so it's a container for the layout
        """
        # TODO: From layouts
        self.widgetHider = QtWidgets.QFrame()
        self.widgetHider.setContentsMargins(0, 0, 0, 0)
        self.hiderLayout = QtWidgets.QVBoxLayout(self.widgetHider)
        self.hiderLayout.setContentsMargins(*self.contentMargins)
        self.hiderLayout.setSpacing(self.contentSpacing)
        self.widgetHider.setHidden(self.collapsed)
        self.widgetHider.setStyleSheet("QFrame {{background-color: rgb{};}}".format(str(self.itemTint)))


    def onCollapsed(self):
        self.widgetHider.setHidden(True)
        self.iconButton.setIcon(self._collapsedIcon)
        self.closeRequested.emit()
        self.collapsed = 1

    def onExpand(self):
        self.widgetHider.setHidden(False)
        self.iconButton.setIcon(self._expandIcon)
        self.openRequested.emit()
        self.collapsed = 0

    def expand(self):
        """ Extra Code for convenience """
        self.onExpand()

    def collapse(self):
        """ Extra Code for convenience """
        self.onCollapsed()

    def showHideWidget(self, *args):
        """Shows and hides the widget `self.widgetHider` this contains the layout `self.hiderLayout`
        which will hold the custom contents that the user specifies
        """

        # TODO: From layouts
        if not self.collapsable:
            return
        # If we're already collapsed then expand the layout
        if self.collapsed:
            self.expand()
            self.updateSize(self)
            return
        self.onCollapsed()
        self.updateSize(self)


    def addMainWidget(self, widget):
        self.hiderLayout.addWidget(widget)
        QtWidgets.QApplication.processEvents()

    def setComboToText(self, combobox, text):
        index = combobox.findText(text, QtCore.Qt.MatchFixedString)
        combobox.setCurrentIndex(index)

    def deleteEvent(self):
        self.deletePressed.emit()
        #self.stackWidget.deleteItem(self)
        

    def updateSize(self, wgt=None):
        if wgt is None:
            wgt = self

        self.updateRequested.emit()
        #if self.stackTableWgt is not None:
        #    self.stackTableWgt.updateSize(wgt)


    def getTitle(self):
        return self.stackTitleWgt.text()

    def setTitle(self, text):
        self.stackTitleWgt.setText(text)

    def titleValidate(self):
        """
        Removes invalid characters and replaces spaces with underscores
        :return:
        """
        if self.spacesToUnderscore:
            nameWgt = self.stackTitleWgt
            text = self.stackTitleWgt.text()
            pos = nameWgt.cursorPosition()

            text = text.replace(" ", "_")
            nameWgt.blockSignals(True)
            nameWgt.setText(text)
            nameWgt.blockSignals(False)

            # set cursor back to original position
            nameWgt.setCursorPosition(pos)

    def parentComboActivated(self):
        parentText = self.parentComboBox.currentText()

        parentComponent = None
        for c in self.core.components():
            if c.name() == parentText:
                parentComponent = c
                break

        if parentComponent is None:
            componentLayer = self.core.currentRig.getOrCreateComponentLayer()
            self.component.setParent(componentLayer)
            return

        self.component.setParent(parentComponent)

    def setFrameColor(self, color):
        style = """
            QFrame, QToolButton
            {{
                background-color: rgb{0};
                border-radius: 3px;
                border: 1px solid rgb{0};

            }}
            QLineEdit
            {{
                background-color: rgb{1};
            }}
            """.format(str(color), str((63, 63, 63)))



        self.titleFrame.setStyleSheet(style)

    def test(self):
        print("test")
        menu = QtWidgets.QMenu()
        menu.addAction("Test")
        menu.addAction("Test")
        menu.addAction("Test")
        #menu.show()
        #menu.popup(QtCore.QPoint(0,0))
        menu.exec_(QtCore.QPoint(50,50))





    def connections(self):
        """toggle widgetHider vis
        """

        """ Connections for the stack items"""
        #self.openRequested.connect(self.stackTableWgt.updateSize)
        #self.closeRequested.connect(self.stackTableWgt.updateSize)

        self.iconButton.clicked.connect(self.showHideWidget)
        self.itemIcon.clicked.connect(self.test)

        self.titleFrame.mouseReleased.connect(self.showHideWidget)

        self.shiftUpBtn.clicked.connect(self.shiftUp)
        self.shiftDownBtn.clicked.connect(self.shiftDown)
        self.deleteBtn.clicked.connect(self.deleteEvent)

        self.stackTitleWgt.textChanged.connect(self.titleValidate)