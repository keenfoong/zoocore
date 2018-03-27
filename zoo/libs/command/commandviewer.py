from qt import QtWidgets
from zoo.libs.iconlib import icon
from zoo.libs.command import executor


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
        self.setup()

    def refresh(self):
        self.listWidget.clear()
        self.setup()

    def setup(self):
        for command in self.executor.commands.values():
            uiData = command.uiData
            item = QtWidgets.QListWidgetItem()
            item.setText(uiData.get("label", ""))
            item.setIcon(icon("icon"))
            self.listWidget.addItem(item)


windowInstance = None


def launch(parent=None):
    global windowInstance
    try:
        windowInstance.close()
    except (RuntimeError, AttributeError):
        pass
    exe = executor.Executor()
    exe.registerEnv("ZOO_COMMAND_LIB")
    windowInstance = CommandViewer(exe, parent=parent)
    windowInstance.show()
    return windowInstance
