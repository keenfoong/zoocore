import math

from qt import QtWidgets, QtCore, QtGui
from zoo.libs.pyqt.widgets.graphics import graphicitems


class GraphicsView(QtWidgets.QGraphicsView):
    contextMenuRequest = QtCore.Signal(object)
    clearSelectionRequest = QtCore.Signal()
    gridSize = 30
    backgroundColor = QtGui.QColor(50, 50, 50)
    gridColor = QtGui.QColor(200, 200, 200)
    gridLineWidth = 1
    overlayAxisPen = QtGui.QPen(QtGui.QColor(255, 50, 50, 255), gridLineWidth)
    thinGridLinePen = QtGui.QPen(QtGui.QColor(80, 80, 80, 255), 0.5)
    selectionRectOutlinerPen = QtGui.QPen(QtGui.QColor(70, 70, 150)),
    selectionRectColor = QtGui.QColor(60, 60, 60, 150),

    def __init__(self, parent=None, setAntialiasing=True):
        super(GraphicsView, self).__init__(parent)

        if setAntialiasing:
            self.setAntialiasing(True)

        # apply default settings
        self.setCacheMode(self.CacheBackground)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setInteractive(True)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenu)
        self.drawGrid = True
        self.pan_active = False
        self.previousMousePos = QtCore.QPointF()
        self.rubberBand = None
        self.currentSelection = []

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)

    def centerPosition(self):
        return self.mapToScene(QtCore.QPoint(self.width() * 0.5, self.height() * 0.5))

    def setAntialiasing(self, aa):
        """ enables or disables antialiaising

        :param aa : bool
        @note This will not effect items that specify their own antialiasing
        """
        if aa:
            self.setRenderHints(self.renderHints() | QtGui.QPainter.Antialiasing)
            return
        self.setRenderHints(self.renderHints() & ~QtGui.QPainter.Antialiasing)

    def mousePressEvent(self, event):
        button = event.buttons()
        if button == QtCore.Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                item.selected = True
                self.currentSelection = [item]
            else:
                for i in self.currentSelection:
                    i.selected = False
                self.rubberBand = graphicitems.SelectionRect(self.mapToScene(event.pos()))
                scene = self.scene()
                scene.addItem(self.rubberBand)
                # self.rubberBand.show()
            self.previousMousePos = event.pos()
        elif event.button() == QtCore.Qt.MiddleButton:
            self.pan_active = True
            self.previousMousePos = self.mapToScene(event.pos()).toPoint()
            self.setCursor(QtCore.Qt.OpenHandCursor)
        elif button == QtCore.Qt.RightButton:
            self._contextMenu(event.pos())
        super(GraphicsView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pan_active:
            delta = self.mapToScene(event.pos()) - self.previousMousePos
            rect = self.sceneRect()
            rect.translate(-delta.x(), -delta.y())
            self.setSceneRect(rect)
            self.previousMousePos = self.mapToScene(event.pos()).toPoint()
            return
        if not self.previousMousePos.isNull() and self.rubberBand:
            self.rubberBand.setDragPoint(self.mapToScene(event.pos()))
        super(GraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.rubberBand:
            self.rubberBand.close()
            self.scene().removeItem(self.rubberBand)
        elif self.pan_active:
            self.pan_active = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        super(GraphicsView, self).mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Tab:
            self.tabPress.emit(QtWidgets.QCursor.pos())
        elif key == QtCore.Qt.Key_Delete:
            self.deletePress.emit()
        super(GraphicsView, self).keyPressEvent(event)

    def drawMainAxis(self, painter, rect):

        painter.setPen(self.overlayAxisPen)

        xLine, yLine = QtCore.QLineF(), QtCore.QLineF()
        if rect.y() < 0 < (rect.height() - rect.y()):
            xLine = QtCore.QLineF(rect.x(), 0, rect.width() + rect.x(), 0)

        if rect.x() < 0 < (rect.height() - rect.x()):
            yLine = QtCore.QLineF(0, rect.y(), 0, rect.height() + rect.y())

        painter.drawLines([xLine, yLine])

    def frameSelectedItems(self, items):
        # itemsArea = self._getSelectedBoundingbox()
        # self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)
        pass

    def frameSceneItems(self):
        itemsArea = self.scene().itemsBoundingRect()
        self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)

    def getViewRect(self):
        """Return the boundaries of the view in scene coordinates"""
        r = QtCore.QRectF(self.rect())
        return self.viewportTransform().inverted()[0].mapRect(r)

    def _contextMenu(self, pos):
        menu = QtWidgets.QMenu()
        self.contextMenuRequest.emit(menu)
        menu.exec_(self.mapToGlobal(pos))

    def drawBackground(self, painter, rect):
        """
        Draw a grid in the background.
        """

        painter.fillRect(rect, self.backgroundColor)
        if not self.drawGrid:
            return super(GraphicsView, self).drawBackground(painter, rect)
        left = int(rect.left()) - (int(rect.left()) % self.gridSize)
        top = int(rect.top()) - (int(rect.top()) % self.gridSize)

        # Draw horizontal fine lines
        gridLines = []
        painter.setPen(self.thinGridLinePen)
        y = float(top)
        while y < float(rect.bottom()):
            gridLines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
            y += self.gridSize
        painter.drawLines(gridLines)

        # Draw vertical fine lines
        gridLines = []
        painter.setPen(self.thinGridLinePen)
        x = float(left)
        while x < float(rect.right()):
            gridLines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
            x += self.gridSize
        painter.drawLines(gridLines)
        # main axis
        self.drawMainAxis(painter, rect)
        return super(GraphicsView, self).drawBackground(painter, rect)
