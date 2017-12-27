from qt import QtWidgets, QtGui, QtCore
from zoo.libs import iconlib
from zoo.libs.pyqt.widgets import frame


class ColorAction(QtWidgets.QWidgetAction):
    def __init__(self, actionData, parent):
        super(ColorAction, self).__init__(parent)
        widget = QtWidgets.QWidget(parent)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        button = QtWidgets.QPushButton(actionData.get("label", ""), parent=widget)
        button.setStyleSheet(
            "QLabel {" + " background-color: {}; color: {};".format(actionData.get("backgroundColor", ""),
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


class SliderAction(QtWidgets.QWidgetAction):

    def __init__(self, label="", parent=None):
        """
        :type parent: QtWidgets.QMenu
        """
        QtWidgets.QWidgetAction.__init__(self, parent)

        self.widget = frame.QFrame(parent)
        self.label = QtWidgets.QLabel(label, self.widget)

        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.widget)
        self._slider.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        self.valueChanged = self._slider.valueChanged

    def createWidget(self, menu):
        """
        This method is called by the QWidgetAction base class.

        :type menu: QtWidgets.QMenu
        """
        actionWidget = self.widget
        actionLayout = QtWidgets.QHBoxLayout(actionWidget)
        actionLayout.setContentsMargins(0, 0, 0, 0)
        actionLayout.addWidget(self.label)
        actionLayout.addWidget(self.slider)
        actionWidget.setLayout(actionLayout)

        return actionWidget
