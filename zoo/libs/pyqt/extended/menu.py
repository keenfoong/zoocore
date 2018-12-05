from qt import QtWidgets, QtCore


class Menu(QtWidgets.QMenu):
    mouseButtonClicked = QtCore.Signal(object, object)  # emits (mouseButton, QAction)

    def mouseReleaseEvent(self, event):
        """ Emit signal for other mouse events like middle and right click for Menu Items

        :param event:
        :type event: QtGui.QMouseEvent
        :return:
        """
        self.mouseButtonClicked.emit(event.button(), self.actionAt(event.pos()))

        return super(Menu, self).mouseReleaseEvent(event)

