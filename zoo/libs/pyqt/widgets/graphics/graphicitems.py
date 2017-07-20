from zoo.libs.pyqt.qt import QtWidgets, QtGui, QtCore


class ItemContainer(QtWidgets.QGraphicsWidget):
    def __init__(self, orientation=QtCore.Qt.Vertical, parent=None):
        super(ItemContainer, self).__init__(parent=parent)
        layout = QtWidgets.QGraphicsLinearLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setOrientation(orientation)
        self.setLayout(layout)

    def setItem(self, item, alignment=None):
        """Adds a QWidget to the container layout
        :param item:
        """
        self.layout().addItem(item)
        if alignment:
            self.layout().setAlignment(item, alignment)


class TextContainer(QtWidgets.QGraphicsWidget):
    def __init__(self, text, *args, **kwargs):
        super(TextContainer, self).__init__(*args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        layout = QtWidgets.QGraphicsLinearLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setOrientation(QtCore.Qt.Horizontal)
        self.setLayout(layout)

        self.title = GraphicsText(text, parent=self)
        layout.addItem(self.title)
        layout.setAlignment(self.title, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

    @property
    def text(self):
        return self._title

    @text.setter
    def text(self, title):
        self.title.text = title


class CubicPath(QtWidgets.QGraphicsPathItem):
    contextMenuRequested = QtCore.Signal(object)
    defaultColor = QtGui.QColor(138, 200, 0)
    selectedColor = QtGui.QColor(255, 255, 255)
    hoverColor = QtGui.QColor(255, 255, 255)

    def __init__(self, sourcePoint, destinationPoint=None):
        super(CubicPath, self).__init__()

        self.sourcePoint = sourcePoint
        self.destinationPoint = destinationPoint
        self.defaultPen = QtGui.QPen(self.defaultColor, 1.25, style=QtCore.Qt.DashLine)
        self.defaultPen.setDashPattern([1, 2, 2, 1])
        self.selectedPen = QtGui.QPen(self.selectedColor, 1.7, style=QtCore.Qt.DashLine)
        self.selectedPen.setDashPattern([1, 2, 2, 1])

        self.hoverPen = QtGui.QPen(self.hoverColor, 1.7, style=QtCore.Qt.DashLine)
        self.selectedPen.setDashPattern([1, 2, 2, 1])
        self.hovering = False

        self.setPen(self.defaultPen)
        self.setZValue(-1)
        self.setFlags(self.ItemIsFocusable | self.ItemIsSelectable | self.ItemIsMovable)
        if self._sourcePort and self._destinationPort:
            self.updatePath()
        self.update()

    def hoverLeaveEvent(self, event):
        super(CubicPath, self).hoverEnterEvent(event)
        self.hovering = False
        self.update()

    def hoverEnterEvent(self, event):
        super(CubicPath, self).hoverEnterEvent(event)
        self.hovering = True
        self.update()

    def paint(self, painter, option, widget):
        if self.isSelected():
            painter.setPen(self.selectedPen)
        elif self.hovering:
            painter.setPen(self.hoverPen)
        else:
            painter.setPen(self.defaultPen)
        painter.drawPath(self.path())

    def updatePath(self):

        path = QtGui.QPainterPath()
        path.moveTo(self.sourcePoint)
        ctrl1 = QtCore.QPointF(self.sourcePoint.x(), self.sourcePoint.y())
        path.cubicTo(ctrl1, ctrl1, self.destinationPoint)
        self.setPath(path)

    def setSourcePoint(self, point):
        self.sourcePoint = point
        self.updatePath()

    def setDestinationPoint(self, point):
        self.destinationPoint = point
        self.updatePath()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            event.accept()
            if self.isSelected():
                self.setSelected(False)
            else:
                self.setSelected(True)

            self.update()
        self.destinationPoint = event.pos()

    def mouseMoveEvent(self, event):
        self.destinationPoint = event.pos()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete or event.key() == QtCore.Qt.Key_Backspace:
            self.close()
            event.accept()
            return
        event.ignore()

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)

        self.contextMenuRequested.emit(menu)
        menu.exec_(event.scenePos())
        event.setAccepted(True)


class SelectionRect(QtWidgets.QGraphicsWidget):
    def __init__(self, pen, color, mouseDownPos):
        super(SelectionRect, self).__init__()
        self.setZValue(-1)
        self._color = color or QtGui.QColor(80, 80, 80, 50)
        self._pen = pen or QtGui.QPen(QtGui.QColor(20, 20, 20), 1.0, QtCore.Qt.DashLine)
        self._mouseDownPos = mouseDownPos
        self.setPos(self._mouseDownPos)

    def setColor(self, color):
        self._color = color
        self.update()

    def setPen(self, pen):
        self._pen = pen
        self.update()

    def setDragPoint(self, dragPoint):
        topLeft = QtCore.QPointF(self._mouseDownPos)
        bottomRight = QtCore.QPointF(dragPoint)
        xdown = self._mouseDownPos.x()
        ydown = self._mouseDownPos.y()
        if dragPoint.x() < xdown:
            topLeft.setX(dragPoint.x())
            bottomRight.setX(xdown)
        if dragPoint.y() < ydown:
            topLeft.setY(dragPoint.y())
            bottomRight.setY(ydown)
        self.setPos(topLeft)
        self.resize(bottomRight.x() - topLeft.x(), bottomRight.y() - topLeft.y())

    def paint(self, painter, option, widget):
        rect = self.windowFrameRect()
        painter.setBrush(self._color)
        painter.setPen(self._pen)
        painter.drawRect(rect)


class GraphicsText(QtWidgets.QGraphicsWidget):
    _font = QtGui.QFont('Helvetica', 8)
    _font.setLetterSpacing(QtGui.QFont.PercentageSpacing, 120)
    _fontMetrics = QtGui.QFontMetrics(_font)

    _color = QtGui.QColor(200, 200, 200)

    def __init__(self, text, parent=None):
        super(GraphicsText, self).__init__(parent=parent)

        self._item = QtWidgets.QGraphicsTextItem(text, parent=self)
        self._item.setDefaultTextColor(self._color)
        self._item.setFont(self._font)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.setPreferredSize(QtCore.QSizeF(self._item.textWidth(), self._font.pointSizeF()))

        self._item.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsFocusable |
                            QtWidgets.QGraphicsItem.ItemIsMovable)
        self._item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)

        option = self._item.document().defaultTextOption()
        self._item.document().setDefaultTextOption(option)
        self.adjustSize()
        self.setPreferredSize(self.size)

    @property
    def text(self):
        return self._item

    @text.setter
    def text(self, text):
        self._item.setPlainText(text)
        self._item.update()
        self.setPreferredSize(QtCore.QSizeF(self._item.textWidth(),
                                            self._font.pointSizeF() + 10))

    def onResize(self, width):
        fmWidth = self._fontMetrics.width(self.item.toPlainText())
        newWidth = min(fmWidth, width)
        if width > fmWidth:
            newWidth = width

        self._item.setTextWidth(newWidth)
        self.setPreferredSize(newWidth, self.textHeight())

    @property
    def size(self):
        return QtCore.QSizeF(self._item.textWidth(), self.height)

    @property
    def height(self):
        return self._item.document().documentLayout().documentSize().height() + 2
