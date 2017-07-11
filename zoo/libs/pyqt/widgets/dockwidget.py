from zoo.libs.pyqt.qt import QtWidgets


class DockWidget(QtWidgets.QDockWidget):
    def __init__(self, parent=None, floating=False):
        super(DockWidget, self).__init__(parent)
        self.setFloating(floating)
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFloatable |
            QtWidgets.QDockWidget.DockWidgetClosable)
