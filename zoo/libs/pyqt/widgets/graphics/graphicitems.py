from qt import QtWidgets, QtGui, QtCore


class ItemContainer(QtWidgets.QGraphicsWidget):
    def __init__(self, orientation=QtCore.Qt.Vertical, parent=None):
        super(ItemContainer, self).__init__(parent=parent)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        layout = QtWidgets.QGraphicsLinearLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setOrientation(orientation)
        self.setLayout(layout)

    def items(self):
        layout = self.layout()
        for i in range(layout.count()):
            yield layout.itemAt(i)

    def addItem(self, item, alignment=None):
        """Adds a QWidget to the container layout
        :param item:
        """
        self.layout().addItem(item)
        if alignment:
            self.layout().setAlignment(item, alignment)

    def insertItem(self, index, item, alignment=None):
        self.layout().insertItem(index, item)
        if alignment:
            self.layout().setAlignment(item, alignment)

    def clear(self):
        layout = self.layout()
        for i in range(layout.count()):
            layout.removeAt(i)

    def removeItemAtIndex(self, index):
        """Adds a QWidget to the container layout

        """
        self.prepareGeometryChange()
        layout = self.layout()
        if index in range(self.layout().count()):
            layout.removeAt(index)


class TextContainer(QtWidgets.QGraphicsWidget):
    textChanged = QtCore.Signal(str)

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


class ConnectionEdge(QtWidgets.QGraphicsPathItem):
    contextMenuRequested = QtCore.Signal(object)
    defaultColor = QtGui.QColor(138, 200, 0)
    selectedColor = QtGui.QColor(255, 255, 255)
    hoverColor = QtGui.QColor(255, 255, 255)
    CUBIC = 0
    LINEAR = 1

    def __init__(self, source, destination=None, curveType=CUBIC):
        super(ConnectionEdge, self).__init__()
        self.curveType = curveType
        self._sourcePlug = source
        self._destinationPlug = destination
        self._sourcePoint = source.center()
        self._destinationPoint = destination.center() if destination is not None else None
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
        if self._sourcePlug and self._destinationPlug:
            self.updatePath()
        self.update()

    def setAsLinearPath(self):
        path = QtGui.QPainterPath()
        path.moveTo(self._sourcePoint)
        path.lineTo(self._destinationPoint)
        self.setPath(path)

    def setAsCubicPath(self):
        path = QtGui.QPainterPath()

        path.moveTo(self._sourcePoint)
        dx = self._destinationPoint.x() - self._sourcePoint.x()
        dy = self._destinationPoint.y() - self._sourcePoint.y()
        ctrl1 = QtCore.QPointF(self._sourcePoint.x() + dx * 0.50, self._sourcePoint.y() + dy * 0.1)
        ctrl2 = QtCore.QPointF(self._sourcePoint.x() + dx * 0.50, self._sourcePoint.y() + dy * 0.9)
        path.cubicTo(ctrl1, ctrl2, self._destinationPoint)
        self.setPath(path)

    def hoverLeaveEvent(self, event):
        super(ConnectionEdge, self).hoverEnterEvent(event)
        self.hovering = False
        self.update()

    def hoverEnterEvent(self, event):
        super(ConnectionEdge, self).hoverEnterEvent(event)
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

    def updatePosition(self):
        """Update the position of the start and end of the edge
        """
        self._destinationPoint = self.destinationPlug.center()
        self._sourcePoint = self.sourcePlug.center()
        self.update()

    def updatePath(self):
        if self.curveType == ConnectionEdge.CUBIC:
            self.setAsCubicPath()
        else:
            self.setAsLinearPath()

    def connect(self, src, dest):
        """Create a connection between the src plug and the destination plug
        :param src: Plug
        :param dest: Plug
        :return: None
        """
        if not src and dest:
            return
        self.sourcePlug = src
        self.destinationPlug = dest
        src.addConnection(self)
        dest.addConnection(self)

    def disconnect(self):
        """Remove the connection between the source and destination plug
        """
        self._sourcePlug.removeConnection(self)
        self._sourcePlug.removeConnection(self)
        self._sourcePlug = None
        self._destinationPlug = None

    @property
    def sourcePoint(self):
        """Return the source point
        :return: QtCore.QPointF()
        """
        return self._sourcePoint

    @sourcePoint.setter
    def sourcePoint(self, point):
        """Sets the source point and updates the path
        :param point: QtCore.QPointF
        """
        self._sourcePoint = point
        self.updatePath()

    @property
    def destinationPoint(self):
        """return the destination point
        :return: QtCore.QPointF
        """
        return self._destinationPoint

    @destinationPoint.setter
    def destinationPoint(self, point):
        """Sets the destination point and updates the path
        :param point: QtCore.QPointF
        """
        self._destinationPoint = point
        self.updatePath()

    @property
    def sourcePlug(self):
        """Return the source plug
        :return: Plug
        """
        return self._sourcePlug

    @sourcePlug.setter
    def sourcePlug(self, plug):
        """Sets the source plug and update the path
        :param plug: Plug
        """
        self._sourcePlug = plug
        self._sourcePoint = plug.center()
        if self._destinationPoint:
            self.updatePath()

    @property
    def destinationPlug(self):
        """Returns the destination plug
        :return: Plug
        """
        return self._destinationPlug

    @destinationPlug.setter
    def destinationPlug(self, plug):
        self._destinationPlug = plug
        self._destinationPoint = plug.center()
        if self._sourcePoint:
            self.updatePath()

    def close(self):
        """
        """
        if self.scene() is not None:
            self.scene().removeItem(self)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            event.accept()
            if self.isSelected():
                self.setSelected(False)
            else:
                self.setSelected(True)

            self.update()
        self._destinationPoint = event.pos()

    def mouseMoveEvent(self, event):
        self._destinationPoint = self.mapToScene(event.pos())

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
    def __init__(self, mouseDownPos):
        super(SelectionRect, self).__init__()
        self.setZValue(100)
        self._color = QtGui.QColor(80, 80, 80, 50)
        self._pen = QtGui.QPen(QtGui.QColor(20, 20, 20), 1.0, QtCore.Qt.DashLine)
        self._mouseDownPos = mouseDownPos
        self.setPos(self._mouseDownPos)
        self.resize(0, 0)

    def setColor(self, color):
        self._color = color
        self.update()

    def setPen(self, pen):
        self._pen = pen
        self.update()

    def setStartPoint(self, point):
        self._mouseDownPos = point

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
    _font = QtGui.QFont("Roboto-Bold.ttf", 8)
    _font.setLetterSpacing(QtGui.QFont.PercentageSpacing, 110)
    _fontMetrics = QtGui.QFontMetrics(_font)

    _color = QtGui.QColor(200, 200, 200)

    def __init__(self, text, parent=None):
        super(GraphicsText, self).__init__(parent=parent)

        self._item = QtWidgets.QGraphicsTextItem(text, parent=self)
        self._item.setDefaultTextColor(self._color)
        self._item.setFont(self._font)
        self.setPreferredSize(self.size)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self._item.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsFocusable |
                            QtWidgets.QGraphicsItem.ItemIsMovable)
        self._item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        option = self._item.document().defaultTextOption()
        option.setWrapMode(QtGui.QTextOption.NoWrap)
        self._item.document().setDefaultTextOption(option)
        self.allowHoverHighlight = False
        self.setAcceptHoverEvents(True)
        self.adjustSize()

    def setTextFlags(self, flags):
        self._item.setFlags(flags)

    @property
    def font(self):
        return self._item.font()

    @font.setter
    def font(self, value):
        return self._item.setFont(value)

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

    @property
    def color(self):
        return self._item.defaultTextColor()

    @color.setter
    def color(self, color):
        self._item.setDefaultTextColor(color)
        self.update()

    def highlight(self):
        highlightColor = self.color.lighter(150)
        self.color = highlightColor

    def unhighlight(self):
        self.color = self._color

    def hoverEnterEvent(self, event):
        if self.allowHoverHighlight:
            self.highlight()
        super(GraphicsText, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if self.allowHoverHighlight:
            self.unhighlight()
        super(GraphicsText, self).hoverLeaveEvent(event)
