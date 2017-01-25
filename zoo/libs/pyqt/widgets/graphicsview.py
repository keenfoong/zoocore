import math
from zoo.libs.pyqt.qt import QtWidgets, QtCore


class GraphicsView(QtWidgets.QGraphicsView):
    tabPress = QtCore.Signal(object)
    deletePress = QtCore.Signal()
    contextMenuRequest = QtCore.Signal(object)

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

    def wheelEvent(self, event):
        """
        scale the graph view up and down
        """
        scaleFactor = math.pow(2.0, event.delta() / 240.0)
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 25:
            return
        self.scale(scaleFactor, scaleFactor)
        self.update()

    def setAntialiasing(self, aa):
        """ enables or disables antialiaising

        :param aa : bool
        @note This will not effect items that specify their own antialiasing
        """
        if aa:
            self.setRenderHints(self.renderHints() | QtWidgets.QPainter.Antialiasing)
            return
        self.setRenderHints(self.renderHints() & ~QtWidgets.QPainter.Antialiasing)

    def getViewRect(self):
        """Return the boundaries of the view in scene coordinates"""
        r = QtCore.QRectF(self.rect())
        return self.viewportTransform().inverted()[0].mapRect(r)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Tab:
            self.tabPress.emit(QtWidgets.QCursor.pos())
            return
        elif event.key() == QtCore.Qt.Key_Delete:
            self.deletePress.emit()
        super(GraphicsView, self).keyPressEvent(event)

    def _contextMenu(self, pos):
        menu = QtWidgets.QMenu()
        self.contextMenuRequest.emit(menu)
        menu.exec_(self.mapToGlobal(pos))
