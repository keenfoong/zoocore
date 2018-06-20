import os

from qt import QtWidgets, QtGui, QtCore
from zoo.libs.pyqt import utils as qtutils
from zoo.libs.pyqt.syntaxhighlighter import highlighter


class NumberBar(QtWidgets.QWidget):

    def __init__(self, edit):
        super(NumberBar, self).__init__(edit)

        self.edit = edit
        self.adjustWidth(1)

    def paintEvent(self, event):
        self.edit.numberbarPaint(self, event)
        super(NumberBar,self).paintEvent(event)

    def adjustWidth(self, count):
        width = self.fontMetrics().width(unicode(count))
        if self.width() != width:
            self.setFixedWidth(width)

    def updateContents(self, rect, scroll):
        if scroll:
            self.scroll(0, scroll)
        else:
            self.update()


class TextEditor(QtWidgets.QPlainTextEdit):

    def __init__(self, parent=None):
        super(TextEditor, self).__init__(parent=parent)

        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.highlight()
        self.cursorPositionChanged.connect(self.highlight)

    def highlight(self):
        hi_selection = QtWidgets.QTextEdit.ExtraSelection()

        hi_selection.format.setBackground(self.palette().alternateBase())
        hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        hi_selection.cursor = self.textCursor()
        hi_selection.cursor.clearSelection()

        self.setExtraSelections([hi_selection])

    def numberbarPaint(self, number_bar, event):
        font_metrics = self.fontMetrics()
        current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1

        block = self.firstVisibleBlock()
        line_count = block.blockNumber()
        painter = QtGui.QPainter(number_bar)
        painter.fillRect(event.rect(), self.palette().base())

        # Iterate over all visible text blocks in the document.
        while block.isValid():
            line_count += 1
            block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()

            # Check if the position of the block is out side of the visible
            # area.
            if not block.isVisible() or block_top >= event.rect().bottom():
                break

            # We want the line number for the selected line to be bold.
            if line_count == current_line:
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
            else:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)

            # Draw the line number right justified at the position of the line.
            paint_rect = QtCore.QRect(0, block_top, number_bar.width(), font_metrics.height())
            painter.drawText(paint_rect, QtCore.Qt.AlignRight, unicode(line_count))

            block = block.next()

        painter.end()

class Editor(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(Editor,self).__init__(parent=parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)

        self.textEdit = TextEditor(parent=self)
        self.numberBar = NumberBar(self.textEdit)

        hbox = qtutils.hBoxLayout(parent=self)
        hbox.addWidget(self.numberBar)
        hbox.addWidget(self.textEdit)

        self.textEdit.blockCountChanged.connect(self.numberBar.adjustWidth)
        self.textEdit.updateRequest.connect(self.numberBar.updateContents)
        self.pythonHighlighter = highlighter.highlighterFromJson(os.path.join(os.path.dirname(highlighter.__file__),
                                                                              "highlightdata.json"),
                                                                  self.textEdit.document())
    def text(self):
        return self.textEdit.toPlainText()

    def setText(self, text):
        self.textEdit.setPlainText(text)

    def isModified(self):
        return self.edit.document().isModified()

    def setModified(self, modified):
        self.edit.document().setModified(modified)

    def setLineWrapMode(self, mode):
        self.edit.setLineWrapMode(mode)