from qt import QtWidgets, QtCore

from zoo.libs import iconlib
from zoo.libs.maya.qt import mayaui
from zoo.libs.pyqt import uiconstants
from zoo.libs.pyqt.widgets import frame
from zoo.libs.pyqt.widgets.stackwidget import LineClickEdit


class ToolSetWidget(QtWidgets.QTreeWidget):
    """
    Generic Toolsets
    TODO: WIP
    """
    def __init__(self, parent=None):
        super(ToolSetWidget, self).__init__(parent=parent)

        self.initUi()

    def initUi(self):
        pass


class ToolSetWidgetItem(QtWidgets.QWidget):
    """
    The item in each StackTableWidget.
    Modified version of CollapsableFrameLayout in layouts.py
    """
    _downIcon = iconlib.icon("arrowSingleDown")
    _upIcon = iconlib.icon("arrowSingleUp")
    _deleteIcon = iconlib.icon("xMark")
    _itemIcon = iconlib.icon("stream")
    _collapsedIcon = iconlib.icon("sortClosed")
    _expandIcon = iconlib.icon("sortDown")

    closeRequested = QtCore.Signal()
    openRequested = QtCore.Signal()
    shiftUpPressed = QtCore.Signal()
    shiftDownPressed = QtCore.Signal()
    deletePressed = QtCore.Signal()
    updateRequested = QtCore.Signal()

    def __init__(self, title, parent, collapsed=False, collapsable=True, icon=None, startHidden=False,
                 itemTint=tuple([60, 60, 60]), shiftArrowsEnabled=True, deleteButtonEnabled=True, titleEditable=True):
        super(ToolSetWidgetItem, self).__init__(parent=parent)

        if startHidden:
            self.hide()

        self.itemTint = itemTint

        self._itemIcon = icon or self._itemIcon
        self.stackWidget = parent
        self.hide()

        # Init
        self.itemIcon = QtWidgets.QToolButton(parent=self)
        self.shiftDownBtn = QtWidgets.QToolButton(parent=self)
        self.shiftUpBtn = QtWidgets.QToolButton(parent=self)
        self.deleteBtn = QtWidgets.QToolButton(parent=self)
        #self.stackTitleWgt = QtWidgets.QLineEdit(title)
        self.stackTitleWgt = LineClickEdit(title)
        self.titleExtrasLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout = QtWidgets.QHBoxLayout()


        self.spacesToUnderscore = True

        self.layout = QtWidgets.QVBoxLayout()
        self.title = title
        self.color = uiconstants.DARKBGCOLOR
        self.contentMargins = uiconstants.MARGINS
        self.contentSpacing = uiconstants.SPACING
        self.collapsable = collapsable
        self.collapsed = collapsed
        self.titleFrame = frame.QFrame(parent=self)
        self.iconButton = QtWidgets.QToolButton()

        # Title Frame
        self.widgetHider = QtWidgets.QFrame(parent=self)
        self.hiderLayout = QtWidgets.QVBoxLayout(self.widgetHider)

        if not shiftArrowsEnabled:
            self.shiftDownBtn.hide()
            self.shiftUpBtn.hide()

        if not deleteButtonEnabled:
            self.deleteBtn.hide()

        if not titleEditable:
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
        """
        Set the shift arrows to be visible or not. These arrows allow the StackItem to be shifted upwards or downwards.
        :param visible:
        :return:
        """
        if visible:
            self.shiftDownBtn.show()
            self.shiftUpBtn.show()
        else:
            self.shiftDownBtn.hide()
            self.shiftUpBtn.hide()

    def initUi(self):
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.titleExtrasLayout.setContentsMargins(0, 0, 0, 0)
        self.titleExtrasLayout.setSpacing(0)

        self.buildTitleFrame()

        self.buildHiderWidget()

        self.layout.addWidget(self.titleFrame)
        self.layout.addWidget(self.widgetHider)

        self.itemIcon.setIcon(self._itemIcon)
        self.shiftDownBtn.setIcon(self._downIcon)
        self.shiftUpBtn.setIcon(self._upIcon)
        self.deleteBtn.setIcon(self._deleteIcon)

        iconSize = mayaui.sizeByDpi(QtCore.QSize(12, 12))

        self.deleteBtn.setIconSize(iconSize)
        self.shiftUpBtn.setIconSize(iconSize)
        self.shiftDownBtn.setIconSize(iconSize)

    def buildTitleFrame(self):
        """Builds the title part of the layout with a QFrame widget
        """

        # main dark grey qframe
        self.setFrameColor(self.color)
        self.titleFrame.setContentsMargins(4, 1, 4, 0)

        # the horizontal layout
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.titleFrame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        # the icon and title and spacer
        self.iconButton.setParent(self.titleFrame)
        if self.collapsed:
            self.iconButton.setIcon(self._collapsedIcon)
        else:
            self.iconButton.setIcon(self._expandIcon)

        spacerItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # add to horizontal layout
        self.horizontalLayout.addWidget(self.iconButton)
        self.horizontalLayout.addWidget(self.itemIcon)
        self.horizontalLayout.addItem(spacerItem)
        self.titleFrame.setFixedHeight(self.titleFrame.sizeHint().height())

        self.setMinimumSize(self.titleFrame.sizeHint().width(), self.titleFrame.sizeHint().height()+3)

        self.horizontalLayout.addWidget(self.stackTitleWgt)
        self.horizontalLayout.addLayout(self.titleExtrasLayout)
        self.horizontalLayout.addWidget(self.shiftUpBtn)
        self.horizontalLayout.addWidget(self.shiftDownBtn)
        self.horizontalLayout.addWidget(self.deleteBtn)

        self.horizontalLayout.setStretchFactor(self.stackTitleWgt, 4)

    def shiftUp(self):
        self.shiftUpPressed.emit()

    def shiftDown(self):
        self.shiftDownPressed.emit()

    def addWidget(self, widget):
        self.hiderLayout.addWidget(widget)

    def addLayout(self, layout):
        self.hiderLayout.addLayout(layout)

    def buildHiderWidget(self):
        """Builds widget that is collapsable
        Widget can be toggled so it's a container for the layout
        """
        self.widgetHider.setContentsMargins(0, 0, 0, 0)
        self.hiderLayout.setContentsMargins(*self.contentMargins)
        self.hiderLayout.setSpacing(self.contentSpacing)
        self.widgetHider.setHidden(self.collapsed)
        self.widgetHider.setStyleSheet(".QFrame {{background-color: rgb{};}}".format(str(self.itemTint)))

    def onCollapsed(self):
        """
        Collapse and hide the item contents
        :return:
        """
        self.widgetHider.setHidden(True)
        self.iconButton.setIcon(self._collapsedIcon)
        self.closeRequested.emit()
        self.collapsed = 1

    def onExpand(self):
        """
        Expand the contents and show all the widget data
        :return:
        """
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

    def showHideWidget(self):
        """Shows and hides the widget `self.widgetHider` this contains the layout `self.hiderLayout`
        which will hold the custom contents that the user specifies
        """
        if not self.collapsable:
            return

        # If we're already collapsed then expand the layout
        if self.collapsed:
            self.expand()
            self.updateSize()
            return

        self.onCollapsed()
        self.updateSize()

    def setComboToText(self, combobox, text):
        """
        Find the text in the combobox and sets it to active.
        :param combobox:
        :param text:
        :return:
        """
        index = combobox.findText(text, QtCore.Qt.MatchFixedString)
        combobox.setCurrentIndex(index)

    def deleteEvent(self):
        """
        Delete Button Pressed
        :return:
        """
        self.deletePressed.emit()

    def updateSize(self):
        """
        Update the size of the widget. Usually called by collapse or expand for when the widget contents are hidden
        or shown.
        :return:
        """
        self.updateRequested.emit()

    def getTitle(self):
        """
        Get method for the title text
        :return:
        """
        return self.stackTitleWgt.text()

    def setTitle(self, text):
        """
        Set method to get the title text
        :param text:
        :return:
        """
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

    def connections(self):
        """ Connections for stack items"""

        self.iconButton.clicked.connect(self.showHideWidget)

        self.shiftUpBtn.clicked.connect(self.shiftUp)
        self.shiftDownBtn.clicked.connect(self.shiftDown)
        self.deleteBtn.clicked.connect(self.deleteEvent)

        self.stackTitleWgt.textChanged.connect(self.titleValidate)



