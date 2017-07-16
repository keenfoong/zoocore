"""Mostly placeholder code until i get to doing the customisation
"""
from zoo.libs.pyqt.qt import QtWidgets, QtCore, QtGui


class BackDropTitle(QtWidgets.QGraphicsWidget):
    """Text Graphics item for the graphics back drop
    """
    titleChanged = QtCore.Signal(str)

    def __init__(self, title, color, font, fontMetrics, parent=None):
        super(BackDropTitle, self).__init__(parent=parent)
        self.title = title
        self._fontMetrics = fontMetrics
        self.item = QtWidgets.QGraphicsTextItem(title, parent=parent)
        self.item.setDefaultTextColor(color)
        self.item.setFont(font)
        self.item.setPos(0, 1)
        self.item.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsFocusable |
                           QtWidgets.QGraphicsItem.ItemIsMovable)
        self.item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        option = self.item.document().defaultTextOption()
        self.item.document().setDefaultTextOption(option)
        self.item.setTextWidth(140)
        self.adjustSize()
        self.setPreferredSize(self.size)

    def setText(self, text):
        self.item.setPlainText(text)
        self.titleChanged.emit(text)

    def onResize(self, width):
        fmWidth = self._fontMetrics.width(self.item.toPlainText())
        newWidth = min(fmWidth, width)
        if width > fmWidth:
            newWidth = width

        self.item.setTextWidth(newWidth)
        self.setPreferredSize(newWidth, self.textHeight())

    @property
    def size(self):
        return QtCore.QSizeF(self.item.textWidth(), self.height)

    @property
    def height(self):
        return self.item.document().documentLayout().documentSize().height() + 2


class BackdropHeaderItem(QtWidgets.QGraphicsWidget):
    _color = QtGui.QColor(255, 255, 255)
    _font = QtGui.QFont('Helvetica', 8)
    _font.setLetterSpacing(QtGui.QFont.PercentageSpacing, 120)
    _fontMetrics = QtGui.QFontMetrics(_font)

    def __init__(self, text, parent=None):
        super(BackdropHeaderItem, self).__init__(parent)

        layout = QtWidgets.QGraphicsLinearLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setOrientation(QtCore.Qt.Horizontal)
        self.setLayout(layout)

        self.titleWidget = BackDropTitle(text, self._color, self._font, self._fontMetrics, parent=self)
        layout.addItem(self.titleWidget)
        layout.setAlignment(self.titleWidget, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

    def setText(self, text):
        self.titleWidget.setText(text)

    def text(self):
        return str(self.titleWidget.item.toPlainText())


class BackDrop(QtWidgets.QGraphicsWidget):
    contextRequested = QtCore.Signal(object)

    def __init__(self, title, width=120, height=80):
        super(BackDrop, self).__init__()
        self.setAcceptHoverEvents(True)
        self._title = title
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)
        # backdrops always appear behind all scene items
        self.setZValue(-10)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

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
        self.header.setText(title)

    def position(self):
        transform = self.transform()
        size = self.size()
        return QtCore.QPointF(transform.dx() + (size.width() * 0.5), transform.dy() + (size.height() * 0.5)).toTuple()

    def color(self):
        return self._color.toTuple()

    def setColor(self, color):
        self._color = color
        self.update()

    def initLayout(self):
        layout = QtWidgets.QGraphicsLinearLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.setLayout(layout)

        # add the header title
        self.header = BackdropHeaderItem(self._title, parent=self)
        layout.addItem(self.header)
        layout.setAlignment(self.header, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.addStretch(1)

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

        tHeight = self.header.size().height() - 3

        darkerColor = self._color.darker(125)
        darkerColor.setAlpha(255)
        painter.setBrush(darkerColor)
        roundingYHeader = rect.width() * roundingX / tHeight
        painter.drawRoundRect(0, 0, rect.width(), tHeight, roundingX, roundingYHeader)
        painter.drawRect(0, tHeight * 0.5 + 2, rect.width(), tHeight * 0.5)

        painter.setBrush(QtGui.QColor(0, 0, 0, 0))
        painter.drawRoundRect(rect, roundingX, roundingY, mode=QtCore.Qt.AbsoluteSize)

        super(BackDrop, self).paint(painter, option, widget)
