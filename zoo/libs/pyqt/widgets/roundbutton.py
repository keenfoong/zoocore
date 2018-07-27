from qt import QtCore, QtGui, QtWidgets

class Method:
    Mask = 0
    StyleSheet = 1

class RoundButton(QtWidgets.QPushButton):
    """
    A nice rounded button. Currently set through fixed size only.


    """

    def __init__(self, parent=None, text=None, icon=None, method=Method.StyleSheet):
        super(RoundButton, self).__init__(parent=parent,text=text, icon=icon)
        self.method = method

    def setMethod(self, method=Method.Mask):
        self.method = method

    def resizeEvent(self, event):
        """

        :param size:
        :return:
        """

        if self.method == Method.Mask:
            self.setMask(QtGui.QRegion(self.rect(), QtGui.QRegion.Ellipse))
        elif self.method == Method.StyleSheet:
            radius = min(self.rect().width()/2, self.rect().width()/2)
            self.setStyleSheet("border-radius: {}px;".format(radius))

        super(RoundButton, self).resizeEvent(event)

