"""Mostly placeholder code until i get to doing the customisation
"""
from qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphicitems


class BackDrop(QtWidgets.QGraphicsWidget):
    contextRequested = QtCore.Signal(object)
    selectionChanged = QtCore.Signal(object, bool)
    color = QtGui.QColor(65, 120, 122, 255)
    selectionPen = QtGui.QPen(color.lighter(150))
    deselectionPen = QtGui.QPen(color.darker(125))

    def __init__(self, title, width=120, height=80):
        super(BackDrop, self).__init__()
        self.setAcceptHoverEvents(True)
        self._title = title
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

        # backdrops always appear behind all scene items
        self.setZValue(-10)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        self._selected = False
        self.brush = QtGui.QColor(65, 120, 122, 255)
        self.initLayout()
        self.setTitle(title)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        self.contextRequested.emit(menu)
        menu.exec_(event.scenePos())
        event.setAccepted(True)

    def title(self):
        return str(self.header.text())

    def setTitle(self, title):
        self.header.text = title

    def position(self):
        transform = self.transform()
        size = self.size()
        return QtCore.QPointF(transform.dx() + (size.width() * 0.5), transform.dy() + (size.height() * 0.5)).toTuple()

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected=True):
        self._selected = selected
        self.update()
        self.selectionChanged.emit(self, selected)

    def initLayout(self):
        layout = QtWidgets.QGraphicsLinearLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.setLayout(layout)

        # add the header title
        self.header = graphicitems.GraphicsText(self._title, parent=self)
        layout.addItem(self.header)
        layout.setAlignment(self.header, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.addStretch(1)

    def mouseMoveEvent(self, event):
        # event.accept()
        if self.selected:
            self.setPos(self.pos() + self.mapToParent(event.pos()) - self.mapToParent(event.lastPos()))
        super(BackDrop, self).mousePressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.selected = True
        super(BackDrop, self).mousePressEvent(event)

    def serialize(self):
        return {
            'name': self.name,
            'position': self.position,
            'size': self.size().toTuple(),
            'color': self.color
        }

    @classmethod
    def deserialize(cls, data):
        size = data["position"]
        c = cls(data["name"], width=size[0], height=size[1])
        c.setColor(QtGui.QColor(data["color"]))
        return c

    def paint(self, painter, option, widget):
        if self.selected:
            standardPen = self.selectionPen
        else:
            standardPen = self.deselectionPen
        rect = self.windowFrameRect()
        rounded_rect = QtGui.QPainterPath()
        rounded_rect.addRoundRect(rect,
                                  int(150.0 * self.cornerRounding / rect.width()),
                                  int(150.0 * self.cornerRounding / rect.height()))
        painter.strokePath(rounded_rect, standardPen)
        # horizontal line
        labelRect = QtCore.QRectF(rect.left(), rect.top(), rect.width(), 20)
        # node background
        painter.setBrush(self.backgroundColour)
        roundingY = self.cornerRounding
        roundingX = rect.height() / rect.width() * roundingY

        painter.drawRoundRect(rect, roundingX, roundingY)
        painter.setPen(standardPen)
        painter.drawLine(labelRect.bottomLeft(), labelRect.bottomRight())

        super(BackDrop, self).paint(painter, option, widget)

    def getCorner(self, pos):
        topLeft = self.mapFromItem(self, self.boundingRect().topLeft())
        bottomRight = self.mapFromItem(self, self.boundingRect().bottomRight())
        rect = QtCore.QRectF(topLeft, bottomRight)

        if (rect.topLeft() - pos).manhattanLength() < 30:
            return 0
        elif (rect.topRight() - pos).manhattanLength() < 30:
            return 1
        elif (rect.bottomLeft() - pos).manhattanLength() < 30:
            return 2
        elif (rect.bottomRight() - pos).manhattanLength() < 30:
            return 3
        return -1
