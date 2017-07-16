from zoo.libs.pyqt.qt import QtWidgets
from zoo.libs.pyqt.widgets import graphbackdrop
from zoo.libs.pyqt.widgets import graphicsview
from zoo.libs.pyqt.widgets import mainwindow
from zoo.libs.pyqt.widgets.graphics import graphicsScene


class Window(mainwindow.MainWindow):
    def __init__(self, title="test", width=600, height=800, icon="", parent=None, showOnInitialize=True):
        super(Window, self).__init__(title, width, height, icon, parent, showOnInitialize)
        layout = QtWidgets.QVBoxLayout(self)
        self.centralWidget.setLayout(layout)
        self.view = graphicsview.GraphicsView(parent=self)
        self.scene = graphicsScene.GraphicsScene(parent=self)
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        backdrop = graphbackdrop.BackDrop("test backdrop")
        self.scene.addItem(backdrop)