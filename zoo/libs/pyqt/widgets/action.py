from zoo.libs.pyqt.qt import QtWidgets, QtGui
from zoo.libs import iconlib


class ColorAction(QtWidgets.QWidgetAction):
    def __init__(self, actionData, parent):
        super(ColorAction, self).__init__(parent)
        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(2, 2, 2, 2)
        button = QtWidgets.QPushButton(actionData.get("label", ""), parent=widget)
        button.setStyleSheet("QLabel {" + " background-color: {}; color: {};".format(actionData.get("backgroundColor", ""),
                                                                                     actionData.get("color", "")) + "}")
        icon = actionData.get("icon")
        if icon:
            if isinstance(icon, QtGui.QIcon):
                button.setIcon(icon)
            else:
                icon = iconlib.icon(icon)
                if not icon.isNull():
                    button.setIcon(icon)
        button.setToolTip(actionData.get("tooltip", ""))
        button.clicked.connect(self.triggered.emit)
        layout.addWidget(button)
        self.setDefaultWidget(widget)
