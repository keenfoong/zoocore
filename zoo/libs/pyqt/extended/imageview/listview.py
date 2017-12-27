from qt import QtGui, QtCore, QtWidgets
from zoo.libs.pyqt.extended.imageview import model


class ListView(QtWidgets.QListView):
    requestZoom = QtCore.Signal(float)

    def __init__(self, parent=None):
        super(ListView, self).__init__(parent=parent)

        self.setMouseTracking(True)
        self.setSelectionRectVisible(True)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, event):
        modifiers = event.modifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            self.requestZoom.emit(event.delta())
            vbar = self.verticalScrollBar()
            sliderMax = vbar.maximum()
            sliderPos = vbar.sliderPosition()

            if sliderPos != sliderMax:
                return
        super(ListView, self).wheelEvent(event)


class ExtendedItemView(QtWidgets.QWidget):
    zoomAmount = 90
    default_min_icon_size = 50

    def __init__(self, parent=None):
        super(ExtendedItemView, self).__init__(parent)

        self.qModel = None
        self.initUi()
        self.iconSize = QtCore.QSize(256, 256)

    def initUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.listView = ListView(parent=self)
        delegate = model.ThumbnailDelegate(self)
        self.listView.setItemDelegate(delegate)
        layout.addWidget(self.listView)

        self.listView.verticalScrollBar().valueChanged.connect(self.paginationLoadNextItems)
        self.listView.requestZoom.connect(self._calculateZoom)

    def closeEvent(self, *args, **kwargs):
        for item in self.listView.model().items:
            if item.loaderThread.isRunning():
                item.loaderThread.wait()
        super(ExtendedItemView, self).closeEvent(*args, **kwargs)

    def setModel(self, model):
        self.listView.setModel(model)
        self.qModel = model
        model.view = self

    def invisibleRootItem(self):
        if self.qModel:
            return self.qModel.invisibleRootItem()
        return

    def _calculateZoom(self, delta):
        inFactor = 1.15
        outFactor = 1 / inFactor

        if delta > 0:
            zoomFactor = inFactor
        else:
            zoomFactor = outFactor
        self.setZoomAmount(zoomFactor)

    def setZoomAmount(self, value):
        self.zoomAmount = value
        currentSize = self.iconSize
        currentSize.setWidth(currentSize.width() * value)
        currentSize.setHeight(currentSize.height() * value)
        self.setIconSize(currentSize)

    def setIconSize(self, size):
        self.iconSize = size
        self.listView.setIconSize(size)

    def paginationLoadNextItems(self):
        if self.qModel is None:
            return

        vbar = self.listView.verticalScrollBar()
        sliderMax = vbar.maximum()
        sliderPos = vbar.sliderPosition()

        if sliderPos == sliderMax:
            self.qModel.loadData()
