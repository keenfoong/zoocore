
from qt import QtWidgets, QtCore, QtGui
from zoo.libs import iconlib

from zoo.libs.pyqt.widgets import layouts

class StackWidget(QtWidgets.QWidget):
    """
    The overall layout widget
    """
    _expandIcon = iconlib.icon("roundedsquare")
    _collapseIcon = iconlib.icon("minus")

    def __init__(self, parent):
        super(StackWidget, self).__init__()

        self.stackTableWgt = StackTableWidget(self)
        self.stackItems = self.stackTableWgt.stackItems
        self.stackSearchEdit = QtWidgets.QLineEdit()
        self.collapseBtn = QtWidgets.QPushButton()
        self.expandBtn = QtWidgets.QPushButton()
        self.initUi()

        self.connections()

    def initUi(self):

        compStackToolbar = QtWidgets.QHBoxLayout()
        compStackToolbar.addWidget(self.stackSearchEdit)

        self.expandBtn.setIcon(self._expandIcon)
        self.expandBtn.setIconSize(QtCore.QSize(12, 12))

        self.collapseBtn.setIcon(self._collapseIcon)
        self.collapseBtn.setIconSize(QtCore.QSize(10, 10))

        size = QtCore.QSize(self.collapseBtn.sizeHint().width(), 20) # Temporary size till we get icons here
        self.collapseBtn.setFixedSize(size)
        self.expandBtn.setFixedSize(size)

        compStackToolbar.addWidget(self.collapseBtn)
        compStackToolbar.addWidget(self.expandBtn)
        compStackToolbar.setStretchFactor(self.stackSearchEdit, 1)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(QtWidgets.QLabel("Installed Components"))
        mainLayout.addLayout(compStackToolbar)
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
        text = self.stackTableWgt.text().lower()
        self.stackTableWgt.filter(text)
        self.stackTableWgt.updateSize()

    def clearStack(self):
        self.stackTableWgt.clearStack()

    def addStackItem(self, item):
        self.stackTableWgt.addStackItem(item)

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

    DEFAULT_MAYA_COLOUR = (68, 68, 68)
    def __init__(self, parent=None):
        super(StackTableWidget, self).__init__(parent)

        self.stackItems = []
        self.initUi()
        self.setShowGrid(False)
        self.cellPadding = 5

        style = """
            QTableView {{
            background-color: rgb{0};
            border-size: 0px;
            }}

            QTableView:item {{
            padding:{1}px;
            border-size: 0px;
            }}
            """.format(str(self.DEFAULT_MAYA_COLOUR), self.cellPadding)

        self.setStyleSheet(style)

    def initUi(self):
        self.setRowCount(0)
        self.setColumnCount(1)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()

        self.horizontalHeader().setStretchLastSection(True)

        self.setContentsMargins(2, 2, 2, 2)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def shiftTableItem(self, wgt, dir):
        # Update componentList
        #self.shiftComponentStack(wgt, dir)

        row = self.getRow(wgt)

        if row == 0 and dir == -1 or \
                                row == self.rowCount() - 1 and dir == 1:
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

        print (self.stackItems)
        row = self.getRow(wgt)
        self.removeRow(row)
        self.stackItems.remove(wgt)

        wgt.deleteLater()

    def addStackItem(self, item):
        self.stackItems.append(item)
        self.addRow(item)
        self.updateSize()
        self.updateWidgets()

    def addRow(self, stackItem):
        rowPos = self.rowCount()
        self.setRowCount(rowPos + 1)
        self.setItem(rowPos, 0, QtWidgets.QTableWidgetItem())
        self.setCellWidget(rowPos, 0, stackItem)
        self.updateSize(stackItem)
        self.setRowHeight(rowPos, stackItem.sizeHint().height() + 100)

    def getRow(self, stackItem):
        for i in range(self.rowCount()):
            if stackItem == self.cellWidget(i, 0):
                return i

    def filter(self, text):
        for i in range(self.rowCount()):
            found = not (text in self.cellWidget(i, 0).component.name().lower())
            self.setRowHidden(i, found)

    def updateWidgets(self):
        for c in self.stackItems:
            c.updateUi()

    def getStackItems(self):
        # stackItems = [self.stackLayout.itemAt(i) for i in range(self.stackLayout.count())]
        return self.stackItems

    def updateSize(self, forceComponent=None):

        if forceComponent is not None:
            stackItem = forceComponent
        else:
            stackItem = self.sender()

            if stackItem is None:
                return

        newHeight = stackItem.sizeHint().height() + self.cellPadding * 2
        self.setRowHeight(self.getRow(stackItem), newHeight)

    def clearStack(self):
        self.stackItems = []
        self.clear()
        self.setRowCount(0)

    def sceneRefresh(self):
        self.clearStack()


class StackItem(layouts.CollapsableFrameLayout):
    _downIcon = iconlib.icon("arrowSingleDown")
    _upIcon = iconlib.icon("arrowSingleUp")
    _deleteIcon = iconlib.icon("xMark")
    _itemIcon = iconlib.icon("fkcomponentsimple")

    def __init__(self, title, collapsed=False, collapsable=True, parent=None):
        self.stackWidget = parent
        self.stackTableWgt = parent.stackTableWgt

        # Init
        self.itemIcon = QtWidgets.QToolButton()
        self.shiftDownBtn = QtWidgets.QToolButton()
        self.shiftUpBtn = QtWidgets.QToolButton()
        self.deleteBtn = QtWidgets.QToolButton()
        self.stackTitleWgt = QtWidgets.QLineEdit(title)


        self.spacesToUnderscore = True

        super(StackItem, self).__init__(title=title, collapsed=collapsed, collapsable=collapsable,
                                                 parent=parent)

        # self.initUi()

    def initUi(self):
        super(StackItem, self).initUi()

        self.itemIcon.setIcon(self._itemIcon)
        self.shiftDownBtn.setIcon(self._downIcon)
        self.shiftUpBtn.setIcon(self._upIcon)
        self.deleteBtn.setIcon(self._deleteIcon)

        self.deleteBtn.setIconSize(QtCore.QSize(12, 12))
        self.shiftUpBtn.setIconSize(QtCore.QSize(12, 12))
        self.shiftDownBtn.setIconSize(QtCore.QSize(12, 12))
        # self.itemIcon.setIconSize(QtCore.QSize(24, 24))

        self.horizontalLayout.insertWidget(1, self.itemIcon)
        self.horizontalLayout.addWidget(self.shiftUpBtn)
        self.horizontalLayout.addWidget(self.shiftDownBtn)
        self.horizontalLayout.addWidget(self.deleteBtn)

        # Possibly should tweak layouts.CollapsableFrameLayout (or create a new class) instead of adding then deleting
        i = self.horizontalLayout.indexOf(self.titleLabel)
        self.horizontalLayout.takeAt(i)
        self.titleLabel.deleteLater()
        self.horizontalLayout.insertWidget(2, self.stackTitleWgt)
        self.horizontalLayout.setStretchFactor(self.stackTitleWgt, 4)

        self.itemConnections()

    def shiftUp(self):
        self.stackWidget.shiftItem(self, -1)

    def shiftDown(self):
        self.stackWidget.shiftItem(self, 1)

    def expand(self):
        self.onExpand()

    def collapse(self):
        self.onCollapsed()

    def setComboToText(self, combobox, text):
        index = combobox.findText(text, QtCore.Qt.MatchFixedString)
        combobox.setCurrentIndex(index)

    def deleteEvent(self):
        self.stackWidget.deleteItem(self)

    def itemConnections(self):
        self.openRequested.connect(self.stackTableWgt.updateSize)
        self.closeRequested.connect(self.stackTableWgt.updateSize)

        self.shiftUpBtn.clicked.connect(self.shiftUp)
        self.shiftDownBtn.clicked.connect(self.shiftDown)
        self.deleteBtn.clicked.connect(self.deleteEvent)

        self.stackTitleWgt.textChanged.connect(self.titleValidate)

    def updateSize(self):
        self.stackTableWgt.updateSize()

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