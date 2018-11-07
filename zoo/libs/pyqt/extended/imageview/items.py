import os

from qt import QtGui, QtCore, QtWidgets
from zoo.libs.pyqt import thread


class ItemSignals(thread.WorkerSignals):
    updated = QtCore.Signal(object)


class ThreadedIcon(QtCore.QRunnable):

    def __init__(self, iconPath, width=None, height=None, *args, **kwargs):
        super(ThreadedIcon, self).__init__(*args, **kwargs)
        self.signals = ItemSignals()
        # Add the callback to our kwargs
        kwargs['progress_callback'] = self.signals.progress

        self._path = iconPath
        self.width = width
        self.height = height
        self.placeHolderImage = QtGui.QImage(200, 200, QtGui.QImage.Format_ARGB32)
        self.placeHolderImage.fill(QtGui.qRgb(255, 0, 0))
        self._finished = False

    def finished(self, state):
        self._finished = state
        self.signals.finished.emit()

    @QtCore.Slot()
    def run(self):
        if not self._path or self._finished:
            return
        self.signals.updated.emit(self.placeHolderImage)
        try:
            image = QtGui.QImage(self._path)
        except Exception as er:
            self.signals.error.emit((er,))
            self.finished(True)
            return
        self.signals.updated.emit(image)
        self.finished(True)


class BaseItem(object):
    def __init__(self, name=None, description=None, iconPath=None):
        self.name = name or ""
        self.iconPath = iconPath or ""
        self._description = description or ""
        self.metadata = {}
        self.user = ""

    def description(self):
        return self._description

    def tags(self):
        return self.metadata.get("metadata", {}).get("tags", [])

    def hasTag(self, tag):
        for i in self.tags:
            if tag in i:
                return True
        return False

    def hasAnyTags(self, tags):
        for i in tags:
            if self.hasTag(i):
                return True
        return False

    def serialize(self):
        return {"metadata": {"time": "",
                             "version": "",
                             "user": "",
                             "name": self.name,
                             "application": {"name": "",
                                             "version": ""},
                             "description": "",
                             "tags": []},
                }


class TreeItem(QtGui.QStandardItem):
    backgroundColor = QtGui.QColor(70, 70, 80)
    backgroundColorSelected = QtGui.QColor(50, 180, 240)
    backgroundColorHover = QtGui.QColor(50, 180, 150)
    textColorSelected = QtGui.QColor(255, 255, 255)
    textColor = QtGui.QColor(255, 255, 255)
    backgroundBrush = QtGui.QBrush(backgroundColor)
    backgroundColorSelectedBrush = QtGui.QBrush(backgroundColorSelected)
    backgroundColorHoverBrush = QtGui.QBrush(backgroundColorHover)

    def __init__(self, item, parent=None):
        super(TreeItem, self).__init__(parent=parent)
        self.padding = 2.5
        self.textHeight = 15
        self.showText = True
        self._item = item
        self._pixmap = QtGui.QPixmap()
        self.iconSize = QtCore.QSize(256, 256)
        self.loaderThread = ThreadedIcon(item.iconPath)
        self.setEditable(False)

    def item(self):
        return self._item

    def applyFromImage(self, image):
        pixmap = QtGui.QPixmap()
        pixmap = pixmap.fromImage(image)
        self._pixmap = pixmap
        self.model().dataChanged.emit(self.index(), self.index())

    def setIconPath(self, iconPath):
        self._item.iconPath = iconPath
        self._pixmap = QtGui.QPixmap(iconPath)

    def pixmap(self):
        if not self._pixmap.isNull():
            return self._pixmap
        elif not os.path.exists(self._item.iconPath):
            return QtGui.QPixmap()
        return self._pixmap

    def toolTip(self):
        return self._item.description()

    def isEditable(self, *args, **kwargs):
        return False

    def iconAlignment(self):
        return QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter

    def sizeHint(self):
        return self.model().view.iconSize()

    def font(self, index):
        return QtGui.QFont("Courier")

    def textAlignment(self, index):
        return QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter

    def removeRow(self, item):
        if item.loaderThread.isRunning:
            item.loaderThread.wait()
        return super(TreeItem, self).removeRow(item)

    def removeRows(self, items):
        for item in items:
            if item.loaderThread.isRunning:
                item.loaderThread.wait()
        return super(TreeItem, self).removeRows(items)

    def paint(self, painter, option, index):
        painter.save()
        self._paintBackground(painter, option, index)
        if self.showText:
            self._paintText(painter, option, index)
        self._paintIcon(painter, option, index)
        painter.restore()

    def _paintText(self, painter, option, index):
        text = self._item.name
        isSelected = option.state & QtWidgets.QStyle.State_Selected
        color = self.textColorSelected if isSelected else self.textColor
        rect = option.rect
        width = rect.width()
        height = rect.height()
        padding = self.padding
        x, y = padding, padding
        rect.translate(x, y)
        rect.setWidth(width - padding)
        rect.setHeight(height - padding)
        font = self.font(index)
        align = QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom
        metrics = QtGui.QFontMetricsF(font)
        textWidth = metrics.width(text)
        # does the text fit? if not cut off the text
        if textWidth > rect.width() - padding:
            text = metrics.elidedText(text, QtCore.Qt.ElideRight, rect.width())

        pen = QtGui.QPen(color)
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(rect, align, text)

    def _paintBackground(self, painter, option, index):
        isSelected = option.state & QtWidgets.QStyle.State_Selected
        isMouseOver = option.state & QtWidgets.QStyle.State_MouseOver
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        if isSelected:
            brush = self.backgroundColorSelectedBrush
        elif isMouseOver:
            brush = self.backgroundColorHoverBrush
        else:
            brush = self.backgroundBrush
        painter.setBrush(brush)
        painter.drawRect(option.rect)

    def _paintIcon(self, painter, option, index):
        rect = self.iconRect(option)
        pixmap = self.pixmap()
        if pixmap.isNull():
            return
        pixmap = pixmap.scaled(
            rect.width(),
            rect.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )

        pixmapRect = QtCore.QRect(rect)
        pixmapRect.setWidth(pixmap.width())
        pixmapRect.setHeight(pixmap.height())

        x = float(rect.width() - pixmap.width()) * 0.5
        y = float(rect.height() - pixmap.height()) * 0.5

        pixmapRect.translate(x, y)
        painter.drawPixmap(pixmapRect, pixmap)

    def iconRect(self, option):
        padding = self.padding
        rect = option.rect
        width = rect.width() - padding
        height = rect.height() - padding
        # deal with the text
        if self.showText:
            height -= self.textHeight
        rect.setWidth(width)
        rect.setHeight(height)

        x = padding + (float(width - rect.width()) * 0.5)
        y = padding + (float(height - rect.height()) * 0.5)
        rect.translate(x, y)
        return rect



