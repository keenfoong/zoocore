from qt import QtWidgets, QtCore, QtGui


class GraphicsView(QtWidgets.QGraphicsView):
    contextMenuRequest = QtCore.Signal(object, object)
    # emitted whenever an event happens that requires the view to update
    updateRequested = QtCore.Signal()
    tabPress = QtCore.Signal(object)
    deletePress = QtCore.Signal(list)

    def __init__(self, config, parent=None, setAntialiasing=True):
        super(GraphicsView, self).__init__(parent)

        if setAntialiasing:
            self.setAntialiasing(True)

        # apply default settings
        self.setCacheMode(self.CacheBackground)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        self.setRenderHint(QtGui.QPainter.NonCosmeticDefaultPen, True)

        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setInteractive(True)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setDragMode(self.RubberBandDrag)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._contextMenu)
        self.config = config
        self.pan_active = False
        self.previousMousePos = QtCore.QPointF()
        self._currentZoomFactor = self.config.zoomFactor

    def wheelEvent(self, event):
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        inFactor = self.config.zoomFactor
        outFactor = 1.0 / inFactor
        zoomFactor = inFactor if event.delta() > 0 else outFactor
        self._currentZoomFactor *= zoomFactor
        if self._currentZoomFactor > self.config.maxZoom:
            self._currentZoomFactor = self.config.maxZoom
            return
        elif self._currentZoomFactor < self.config.minZoom:
            self._currentZoomFactor = self.config.minZoom
            return

        self.scale(zoomFactor, zoomFactor)

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
            # item = self.itemAt(event.pos())
            # if item:
            #     # # if we have the ctrl key pressed then add the selection
            #     if event.modifiers() == QtCore.Qt.ShiftModifier:
            #         if not item.isSelected():
            #             item.setSelected(True)
            #     elif event.modifiers() == QtCore.Qt.ControlModifier and item.isSelected:
            #         item.setSelected(False)
            #     else:
            #         item.setSelected(True)
            # else:
            #     print "bugger"
                # for item in self.scene().selectedItems():
                #     item.setSelected(False)
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
        super(GraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.pan_active:
            self.pan_active = False
            self.setCursor(QtCore.Qt.ArrowCursor)

        super(GraphicsView, self).mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Tab and event.modifiers() == QtCore.Qt.ControlModifier:
            self.tabPress.emit(QtGui.QCursor.pos())
        elif key == QtCore.Qt.Key_Delete:
            self.deletePress.emit(self.scene().selectedItems())
        super(GraphicsView, self).keyPressEvent(event)

    def frameSelectedItems(self):
        selection = self.scene().selectedItems()
        if selection:
            rect = self._getItemsBoundingBox(selection)
        else:
            rect = self.scene().itemsBoundingRect()
        self.fitInView(rect, QtCore.Qt.KeepAspectRatio)

    def _getItemsBoundingBox(self, items):
        bbx = set()
        bby = set()

        for item in items:
            pos = item.scenePos()
            rect = item.boundingRect()
            x, y, = pos.x(), pos.y()
            bbx.add(x)
            bby.add(y)
            bbx.add(x + rect.width())
            bby.add(y + rect.height())

        bbxMax = max(bbx)
        bbxMin = min(bbx)
        bbyMin = min(bby)
        bbyMax = max(bby)
        return QtCore.QRectF(QtCore.QRect(bbxMin, bbyMin, bbxMax - bbxMin, bbyMax - bbyMin))

    def frameSceneItems(self):
        itemsArea = self.scene().itemsBoundingRect()
        self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)

    def getViewRect(self):
        """Return the boundaries of the view in scene coordinates"""
        r = QtCore.QRectF(self.rect())
        return self.viewportTransform().inverted()[0].mapRect(r)

    def _contextMenu(self, pos):
        menu = QtWidgets.QMenu()
        item = self.itemAt(pos)
        self.contextMenuRequest.emit(menu, item)
        if menu.isEmpty():
            return
        menu.exec_(self.mapToGlobal(pos))

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, self.config.graphBackgroundColor)
        if not self.config.drawGrid:
            return super(GraphicsView, self).drawBackground(painter, rect)
        self._drawSubdivisionGrid(painter, rect)
        # main axis
        if self.config.drawMainGridAxis:
            self._drawMainAxis(painter, rect)
        return super(GraphicsView, self).drawBackground(painter, rect)

    def _drawSubdivisionGrid(self, painter, rect):
        left = int(rect.left()) - (int(rect.left()) % self.config.gridSize)
        top = int(rect.top()) - (int(rect.top()) % self.config.gridSize)
        # Draw horizontal fine lines
        gridLines = []
        painter.setPen(self.config.gridColor)
        y = float(top)
        while y < float(rect.bottom()):
            gridLines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
            y += self.config.gridSize
        painter.drawLines(gridLines)

        # Draw vertical fine lines
        gridLines = []
        painter.setPen(self.config.gridColor)
        x = float(left)
        while x < float(rect.right()):
            gridLines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
            x += self.config.gridSize
        painter.drawLines(gridLines)

    def _drawMainAxis(self, painter, rect):

        painter.setPen(self.config.overlayAxisPen)

        xLine, yLine = QtCore.QLineF(), QtCore.QLineF()
        if rect.y() < 0 < (rect.height() - rect.y()):
            xLine = QtCore.QLineF(rect.x(), 0, rect.width() + rect.x(), 0)

        if rect.x() < 0 < (rect.height() - rect.x()):
            yLine = QtCore.QLineF(0, rect.y(), 0, rect.height() + rect.y())

        painter.drawLines([xLine, yLine])
