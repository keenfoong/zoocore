"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
FlowLayout
Custom layout that mimics the behaviour of a flow layout (not supported in PyQt by default)
@source https://qt.gitorious.org/pyside/pyside-examples/source/060dca8e4b82f301dfb33a7182767eaf8ad3d024:examples/layouts/flowlayout.py
Comments added by Jos Balcaen(http://josbalcaen.com/)
@date 1/1/2015

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
from qt import QtWidgets, QtCore


class FlowLayout(QtWidgets.QLayout):
    """Custom layout that mimics the behaviour of a flow layout"""

    def __init__(self, parent=None, margin=0, spacingX=2, spacingY=2):
        """Create a new FlowLayout instance.
        This layout will reorder the items automatically.

        :param parent (QWidget)
        :param margin (int)
        :param spacing (int)
        """
        super(FlowLayout, self).__init__(parent)
        # Set margin and spacing
        if parent is not None:
            self.setMargin(margin)
        self.setSpacing(spacingX)
        self.setSpacingX(spacingX)
        self.setSpacingY(spacingY)
        self.itemList = []

    def __del__(self):
        """Delete all the items in this layout"""
        self.clear()

    def clear(self):
        """
        Clear all widgets
        :return:
        """
        item = self.takeAt(0)
        while item:
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

            item = self.takeAt(0)

    def addItem(self, item):
        """Add an item at the end of the layout.
        This is automatically called when you do addWidget()

        :param item:
        :type item: QWidgetItem
        """
        self.itemList.append(item)

    def count(self):
        """Get the number of items in the this layout

        :return (int)"""
        return len(self.itemList)

    def itemAt(self, index):
        """Get the item at the given index

        :param index (int)
        :return (QWidgetItem)"""
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        """Remove an item at the given index

        :param index (int)
        :return (None)"""
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def insertWidget(self, index, widget):
        """Insert a widget at a given index

        :param index (int)
        :param widget (QWidget)"""
        item = QtWidgets.QWidgetItem(widget)
        self.itemList.insert(index, item)

    def expandingDirections(self):
        """This layout grows only in the horizontal dimension"""
        if QtCore is not None:  # QtCore errors driving me insane
            return QtCore.Qt.Orientations(QtCore.Qt.Horizontal)

    def hasHeightForWidth(self):
        """If this layout's preferred height depends on its width

        :return (boolean) Always True"""
        return True

    def heightForWidth(self, width):
        """Get the preferred height a layout item with the given width

        :param width (int)"""
        if QtCore is not None:  # QtCore errors driving me insane
            height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
            return height

    def setGeometry(self, rect):
        """Set the geometry of this layout

        :param rect (QRect)"""
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        """Get the preferred size of this layout

        :return (QSize) The minimum size"""
        return self.minimumSize()

    def minimumSize(self):
        """Get the minimum size of this layout

        :return (QSize)"""
        # Calculate the size
        if QtCore is not None:
            size = QtCore.QSize()
            for item in self.itemList:
                size = size.expandedTo(item.minimumSize())
            # Add the margins
            size += QtCore.QSize(2, 2)
            return size

    def setSpacingX(self, spacing):
        self.spacingX = spacing

    def setSpacingY(self, spacing):
        self.spacingY = spacing

    def doLayout(self, rect, testOnly):
        """Layout all the items

        :param rect (QRect) Rect where in the items have to be laid out
        :param testOnly (boolean) Do the actual layout"""
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            spaceX = self.spacingX
            spaceY = self.spacingY
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + (spaceY * 2)
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(
                        QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()
