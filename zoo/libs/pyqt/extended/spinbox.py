from qt import QtCore
from qt import QtWidgets

DRAG_NONE = 0
DRAG_HORIZONTAL = 1
DRAG_VERTICAL = 2

CURSOR_NONE = 0
CURSOR_BLANK = 1
CURSOR_ARROWS = 2


class DragSpinBox(QtWidgets.QSpinBox):
    def __init__(self, *args, **kwargs):
        super(DragSpinBox, self).__init__(*args, **kwargs)
        self.defaultValue = 0.0
        self._dragSensitivity = 5  # pixels per step
        self._startSensitivity = 10  # pixel move to start the dragging
        # private vars
        self._lastPos = QtCore.QPoint()
        self._leftover = 0
        self._dragStart = None
        self._firstDrag = False
        self._dragType = DRAG_NONE

    def mousePressEvent(self, event):
        if event.button() & QtCore.Qt.RightButton:
            self.setValue(self.defaultValue)
            return True

    def mouseMoveEvent(self, event):
        stepHolder = self.singleStep()
        if self._dragType:
            if self._dragType == DRAG_HORIZONTAL:
                delta = event.pos().x() - self._lastPos.x()
            else:
                delta = self._lastPos.y() - event.pos().y()

            self._leftover += delta
            self._lastPos = event.pos()

            self.stepBy(int(self._leftover / self._dragSensitivity))
            self._leftover %= self._dragSensitivity

        else:
            if event.buttons() & QtCore.Qt.LeftButton:  # only allow left-click dragging
                if self._dragStart is None:
                    self._dragStart = event.pos()

                if abs(event.x() - self._dragStart.x()) > self._startSensitivity:
                    self._dragType = DRAG_HORIZONTAL
                elif abs(event.y() - self._dragStart.y()) > self._startSensitivity:
                    self._dragType = DRAG_VERTICAL

        self.setSingleStep(stepHolder)

    def mouseReleaseEvent(self, event):
        if self._firstDrag:
            self._firstDrag = False
        elif self._dragType:
            self._dragType = DRAG_NONE
            self._lastPos = QtCore.QPoint()
            self._dragStart = None


class DragDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super(DragDoubleSpinBox, self).__init__(*args, **kwargs)
        self.defaultValue = 0.0
        self._dragSensitivity = 5  # pixels per step
        self._startSensitivity = 10  # pixel move to start the dragging
        # private vars
        self._lastPos = QtCore.QPoint()
        self._leftover = 0
        self._dragStart = None
        self._firstDrag = False
        self._dragType = DRAG_NONE
    def mousePressEvent(self, event):
        if event.button() & QtCore.Qt.RightButton:
            self.setValue(self.defaultValue)
            return True

    def mouseMoveEvent(self, event):
        stepHolder = self.singleStep()
        if self._dragType:
            if self._dragType == DRAG_HORIZONTAL:
                delta = event.pos().x() - self._lastPos.x()
            else:
                delta = self._lastPos.y() - event.pos().y()

            self._leftover += delta
            self._lastPos = event.pos()

            self.stepBy(int(self._leftover / self._dragSensitivity))
            self._leftover %= self._dragSensitivity

        else:
            if event.buttons() & QtCore.Qt.LeftButton:  # only allow left-click dragging
                if self._dragStart is None:
                    self._dragStart = event.pos()

                if abs(event.x() - self._dragStart.x()) > self._startSensitivity:
                    self._dragType = DRAG_HORIZONTAL
                elif abs(event.y() - self._dragStart.y()) > self._startSensitivity:
                    self._dragType = DRAG_VERTICAL

        self.setSingleStep(stepHolder)

    def mouseReleaseEvent(self, event):
        if self._firstDrag:
            self._firstDrag = False
        elif self._dragType:
            self._dragType = DRAG_NONE
            self._lastPos = QtCore.QPoint()
            self._dragStart = None
