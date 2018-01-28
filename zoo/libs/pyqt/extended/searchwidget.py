from qt import QtCore, QtGui, QtWidgets
from zoo.libs import iconlib


class SearchLineEdit(QtWidgets.QLineEdit):
    """Search Widget with two icons one on either side, inherents from QLineEdit
    """
    textCleared = QtCore.Signal()

    def __init__(self, searchPixmap, clearPixmap, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)

        self.clearButton = QtWidgets.QToolButton(self)
        self.clearButton.setIcon(QtGui.QIcon(clearPixmap))
        self.clearButton.setCursor(QtCore.Qt.ArrowCursor)
        self.clearButton.setStyleSheet("QToolButton { border: none; padding: 0px; }")
        self.clearButton.hide()
        self.clearButton.clicked.connect(self.clear)
        self.textChanged.connect(self.updateCloseButton)

        self.searchButton = QtWidgets.QToolButton(self)
        self.searchButton.setIcon(QtGui.QIcon(searchPixmap))
        self.searchButton.setStyleSheet("QToolButton { border: none; padding: 0px; }")

        frameWidth = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.setStyleSheet("QLineEdit { padding-left: %dpx; padding-right: %dpx; } "%(
            self.searchButton.sizeHint().width() + frameWidth + 1,
            self.clearButton.sizeHint().width() + frameWidth + 1))
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(),
                                self.searchButton.sizeHint().width() +
                                self.clearButton.sizeHint().width() + frameWidth * 2 + 2),
                            max(msz.height(),
                                self.clearButton.sizeHint().height() + frameWidth * 2 + 2))

    def resizeEvent(self, event):
        sz = self.clearButton.sizeHint()
        frameWidth = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        rect = self.rect()
        yPos = (rect.bottom() + 1 - sz.height()) * 0.5
        self.clearButton.move(self.rect().right() - frameWidth - sz.width(), yPos)
        self.searchButton.move(self.rect().left() + 1, yPos)

    def updateCloseButton(self, text):
        if text:
            self.clearButton.setVisible(True)
            return
        self.clearButton.setVisible(False)


if __name__ == "__name__":
    app = QtWidgets.QApplication([])
    searchIcon = QtGui.QPixmap(iconlib.icon("magnifier"), 16)
    closeIcon = QtGui.QPixmap(iconlib.icon("code", 16))
    w = SearchLineEdit(searchIcon, closeIcon)
    w.show()
    app.exec_()
