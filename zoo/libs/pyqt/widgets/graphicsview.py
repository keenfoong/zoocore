import math
from zoo.libs.pyqt.qt import QtWidgets, QtCore, QtGui


class GraphicsView(QtWidgets.QGraphicsView):
    contextMenuRequest = QtCore.Signal(object)
    clearSelectionRequest = QtCore.Signal()

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

        self.pan_active = True
        self.sceneOrigin = QtCore.QPointF()

        self.overlayAxisPen = QtGui.QPen(QtGui.QColor(160, 160, 160, 120), 1, QtCore.Qt.DashLine)

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
        modifiers = event.modifiers()
        if button == QtCore.Qt.LeftButton:
            scenePos = self.mapToScene(event.pos())
            transform = self.viewportTransform()
            if not self.scene().itemAt(scenePos, transform):
                if not modifiers:
                    self.clearSelectionRequest.emit()

        elif button == QtCore.Qt.MidButton:
            self.pan_active = True
            self.sceneOrigin = self.mapToScene(event.pos())
        else:
            super(GraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        result = super(GraphicsView, self).mouseReleaseEvent(event)
        if self.pan_active:
            current = self.centerPosition()
            scenepanning = self.mapToScene(event.pos())
            newCenter = current - (scenepanning - self.sceneOrigin)
            self.centerOn(newCenter)
        return result

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Tab:
            self.tabPress.emit(QtWidgets.QCursor.pos())
        elif key == QtCore.Qt.Key_Delete:
            self.deletePress.emit()
        else:
            super(GraphicsView, self).keyPressEvent(event)

    def drawOverlayAxis(self, painter, rect):

        painter.setPen(self.overlayAxisPen)
        xLine, yLine = QtCore.QLineF(), QtCore.QLineF()
        if rect.y() < 0 < (rect.height() - rect.y()):
            xLine = QtCore.QLineF(rect.x(), 0, rect.width() + rect.x(), 0)

        if rect.x() < 0 < (rect.height() - rect.x()):
            yLine = QtCore.QLineF(0, rect.y(), 0, rect.height() + rect.y())

        painter.drawLines([xLine, yLine])

    def drawForeground(self, painter, rect):

        self.drawOverlayAxis(painter, rect)
        return super(GraphicsView, self).drawForeground(painter, rect)

    def getViewRect(self):
        """Return the boundaries of the view in scene coordinates"""
        r = QtCore.QRectF(self.rect())
        return self.viewportTransform().inverted()[0].mapRect(r)

    def _contextMenu(self, pos):
        menu = QtWidgets.QMenu()
        self.contextMenuRequest.emit(menu)
        menu.exec_(self.mapToGlobal(pos))
