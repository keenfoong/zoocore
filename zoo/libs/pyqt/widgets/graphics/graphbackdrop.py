"""Mostly placeholder code until i get to doing the customisation
"""
from zoo.libs.pyqt.qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphicitems


class BackDrop(QtWidgets.QGraphicsWidget):
    contextRequested = QtCore.Signal(object)
    selectionChanged = QtCore.Signal(object, bool)

    def __init__(self, title, width=120, height=80):
        super(BackDrop, self).__init__()
        self.setAcceptHoverEvents(True)
        self._title = title
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        # self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        # backdrops always appear behind all scene items
        self.setZValue(-10)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        self._selected = False
        self._color = QtGui.QColor(65, 120, 122, 255)
        self.brush = QtGui.QColor(65, 120, 122, 255)
        self.pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0)
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

    def color(self):
        return self._color.toTuple()

    def setColor(self, color):
        self._color = color
        self.update()

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
        self.setPos(self.position() + self.mapToParent(event.pos()) - self.mapToParent(event.lastPos()))
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.selected = True

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
        rect = self.windowFrameRect()
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        roundingY = 20.0 / (rect.height() / 80.0)
        roundingX = rect.height() / rect.width() * roundingY

        painter.drawRoundRect(rect, roundingX, roundingY, mode=QtCore.Qt.AbsoluteSize)

        tHeight = self.header.size.height() + 5

        darkerColor = self._color.darker(125)
        darkerColor.setAlpha(255)
        painter.setBrush(darkerColor)
        roundingYHeader = rect.width() * roundingX / tHeight
        painter.drawRoundRect(0, 0, rect.width(), tHeight, roundingX, roundingYHeader)
        painter.drawRect(0, tHeight * 0.5 + 2, rect.width(), tHeight * 0.5)

        painter.setBrush(QtGui.QColor(0, 0, 0, 0))
        painter.drawRoundRect(rect, roundingX, roundingY, mode=QtCore.Qt.AbsoluteSize)

        super(BackDrop, self).paint(painter, option, widget)
