from qt import QtGui, QtCore, QtWidgets
from zoo.libs.pyqt.extended.imageview import model
from zoo.libs.pyqt.widgets import listview


class ListView(listview.ListView):
    requestZoom = QtCore.Signal(object, float)
    # QModelIndex, Treeitem
    requestDoubleClick = QtCore.Signal(object, object)
    zoomAmount = 90
    defaultMinIconSize = 50
    defaultMaxIconSize = 512
    defaultIconSize = QtCore.QSize(256, 256)

    def __init__(self, parent=None):
        super(ListView, self).__init__(parent=parent)
        self.setMouseTracking(True)
        self.setSelectionRectVisible(True)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.zoomable = True
        self._iconSize = QtCore.QSize()
        self.setIconSize(self.defaultIconSize)

        self._delegate = model.ThumbnailDelegate(self)
        self.setItemDelegate(self._delegate)

    def setIconSize(self, size):
        self._iconSize = size
        super(ListView, self).setIconSize(size)

    def wheelEvent(self, event):
        """ Overridden to deal with scaling the listview.

        :type event: ::class:`QEvent`
        """
        modifiers = event.modifiers()
        if self.zoomable and modifiers == QtCore.Qt.ControlModifier:

            self._calculateZoom(event.delta())
            vbar = self.verticalScrollBar()
            sliderMax = vbar.maximum()
            sliderPos = vbar.sliderPosition()

            if sliderPos != sliderMax:
                return
        super(ListView, self).wheelEvent(event)

    def _calculateZoom(self, delta):
        """Calculation of the zoom factor before applying it to the icons via the ::func:`setZoomAmount`

        :param delta: the delta value
        :type delta: float
        :return: the converted delta to zoom factor
        :rtype: float
        """
        inFactor = 1.15
        outFactor = 1 / inFactor

        if delta > 0:
            zoomFactor = inFactor
        else:
            zoomFactor = outFactor
        self.setZoomAmount(zoomFactor)
        return zoomFactor

    def setZoomAmount(self, value):
        """Sets the zoom amount to this view by taking the view iconSize()*value

        :param value:
        :type value:
        :return:
        :rtype:
        """
        self.zoomAmount = value
        currentSize = self.iconSize()
        newSize = currentSize.width() * value
        if newSize < self.defaultMinIconSize or newSize > self.defaultMaxIconSize:
            return
        currentSize.setWidth(newSize)
        currentSize.setHeight(newSize)
        self.requestZoom.emit(newSize, self.zoomAmount)
        self.setIconSize(currentSize)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            index = self.currentIndex()
            model = self.model()
            if model is not None:
                item = model.itemFromIndex(index)
                model.doubleClickEvent(index, item)
                self.requestDoubleClick.emit(index, item)


class ThumbnailViewWidget(QtWidgets.QWidget):
    """The main widget for viewing thumbnails, this runs off a custom QStandardItemModel.
    """

    def __init__(self, parent=None):
        """
        :param parent: the parent widget
        :type parent: QtWidgets.QWidget
        """
        super(ThumbnailViewWidget, self).__init__(parent=parent)
        self.qModel = None
        self.initUi()

    def initUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.listView = ListView(parent=self)
        layout.addWidget(self.listView)
        self.listView.verticalScrollBar().valueChanged.connect(self.paginationLoadNextItems)
        self.listView.contextMenuRequested.connect(self.contextMenu)

    def setModel(self, model):
        self.listView.setModel(model)
        model.view = self
        self.qModel = model

    def invisibleRootItem(self):
        if self.qModel:
            return self.qModel.invisibleRootItem()

    def iconSize(self):
        return self.listView.iconSize()

    def setIconSize(self, size):
        if size == self.listView.iconSize():
            return
        maxSize = self.listView.defaultMaxIconSize
        minSize = self.listView.defaultMinIconSize
        width = size.width()
        height = size.height()
        if width > maxSize or height > maxSize:
            size = QtCore.QSize(maxSize, maxSize)
        elif width < minSize or height > minSize:
            size = QtCore.QSize(minSize, minSize)
        self.listView.setIconSize(size)

    def setIconMinMax(self, size):
        """ Sets the min and max icon size

        :param size: min and max of the the icon size
        :type size: tuple(int, int)
        """
        minSize = size[0]
        maxSize = size[1]
        self.listView.defaultMinIconSize = minSize
        self.listView.defaultMaxIconSize = maxSize
        currentSize = self.listView.iconSize()
        width = currentSize.width()
        height = currentSize.height()
        if width > maxSize or height > maxSize:
            size = QtCore.QSize(maxSize, maxSize)
            self.listView.setIconSize(size)
        elif width < minSize or height > minSize:
            size = QtCore.QSize(minSize, minSize)
            self.listView.setIconSize(size)

    def paginationLoadNextItems(self):
        """Simple method to call the models loadData method when the vertical slider hits the max value, useful to load
        the next page of data on the model.

        """
        model = self.listView.model()
        if model is None:
            return

        vbar = self.listView.verticalScrollBar()
        sliderMax = vbar.maximum()
        sliderPos = vbar.sliderPosition()

        if sliderPos == sliderMax:
            model.loadData()

    def contextMenu(self, items, menu):
        print items, menu
