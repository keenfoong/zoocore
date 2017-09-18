from qt import QtWidgets
from zoo.libs.iconlib import icon


class CommandViewer(QtWidgets.QWidget):
    def __init__(self, executor, parent=None):
        super(CommandViewer, self).__init__(parent=parent)
        self.executor = executor
        layout = QtWidgets.QVBoxLayout(self)
        self.scrollWidget = QtWidgets.QScrollArea(self)
        layout.addWidget(self.scrollWidget)
        scrollLayout = QtWidgets.QVBoxLayout(self)
        self.scrollWidget.setLayout(scrollLayout)
        self.listWidget = QtWidgets.QListWidget(self)
        scrollLayout.addWidget(self.listWidget)
        self.setLayout(layout)

    def refresh(self):
        self.listWidget.clear()
        self.setup()

    def setup(self):
        for command in self.executor.commands:
            uiData = command.uiData
            item = self.listWidget.addItem(uiData.get("label"))
            item.setIcon(icon("icon"))
