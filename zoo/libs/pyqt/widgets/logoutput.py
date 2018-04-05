import logging
from qt import QtGui, QtWidgets, QtCore


class OutputLogDialog(QtWidgets.QWidget):
    """Output dialog

    ::example:
        wid = OutputLogDialog("MyLogWindow")
        wid.show()
        wid.logInfo("helloworld")
        wid.logDebug("helloworld")
        wid.logWarning("helloworld")
        wid.logError("helloworld")
        wid.logCritical("helloworld")

    """
    infoColor = QtGui.QColor(QtCore.Qt.white)
    debugColor = QtGui.QColor("#EEE97B")
    warningColor =QtGui.QColor("#D89614")
    errorColor = QtGui.QColor("#CC0000")
    criticalColor = QtGui.QColor("#CC0000")
    html = """<p style="font-weight:300;color:{};"<span><br>{}<br/></span></p>"""

    def __init__(self, title, parent=None):
        super(OutputLogDialog, self).__init__(parent)
        self.setObjectName('{}OutputLog'.format(title))
        self.setWindowTitle(title)
        self.createLayout()
        # use the built logging module for the levels since that would be more consistent
        self.outputType = logging.INFO

    def createLayout(self):
        """Sets up the layout for the dialog."""

        self.textWidget = QtWidgets.QTextEdit(self)
        self.textWidget.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textWidget.setReadOnly(True)
        self.textWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.outputLogLayout = QtWidgets.QVBoxLayout(self)
        self.outputLogLayout.addWidget(self.textWidget)

        self.setLayout(self.outputLogLayout)

        self.textWidget.customContextMenuRequested.connect(self._onContextMenu)

    def logInfo(self, msg):
        self._write(msg, self.infoColor)

    def logDebug(self, msg):
        if self.outputType == logging.DEBUG:
            self._write(msg, self.debugColor)

    def logWarning(self, msg):
        self._write(msg, self.warningColor)

    def logError(self, msg):
        self._write(msg, self.errorColor)

    def logCritical(self, msg):
        self._write(msg, self.criticalColor)

    def _write(self, msg, color):
        html = self.html.format(color.name(), msg)
        self.textWidget.append(html)

    def _onContextMenu(self):
        self.contextMenu = QtWidgets.QMenu(self)
        selectAllAction = self.contextMenu.addAction("Select All")
        copyAction = self.contextMenu.addAction("Copy")
        clearAction = self.contextMenu.addAction("Clear")
        self.contextMenu.addSeparator()
        selectAllAction.triggered.connect(self.contextSelectAll)
        copyAction.triggered.connect(self.contextCopy)
        clearAction.triggered.connect(self.textWidget.clear)
        self.onContextMenu(self.contextMenu)
        self.contextMenu.exec_(QtGui.QCursor.pos())

    def onContextMenu(self, menu):
        pass

    def contextSelectAll(self):
        self.textWidget.selectAll()

    def contextCopy(self):
        self.textWidget.copy()