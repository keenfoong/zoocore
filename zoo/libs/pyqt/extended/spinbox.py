from qt import QtCore
from qt import QtWidgets


class DragSpinBox(QtWidgets.QSpinBox):
    def __init__(self, *args, **kwargs):
        super(DragSpinBox, self).__init__(*args, **kwargs)

        self.spinner = _SpinBoxDragFilter(self)
        self.spinner.defaultValue = 0.0
        self.installEventFilter(self.spinner)


class DragDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super(DragDoubleSpinBox, self).__init__(*args, **kwargs)

        self.spinner = _SpinBoxDragFilter(self)
        self.spinner.defaultValue = 0.0
        self.installEventFilter(self.spinner)


class _SpinBoxDragFilter(QtCore.QObject):
    DRAG_NONE = 0
    DRAG_HORIZONTAL = 1
    DRAG_VERTICAL = 2

    CURSOR_NONE = 0
    CURSOR_BLANK = 1
    CURSOR_ARROWS = 2

    def __init__(self, *args, **kwargs):
        super(_SpinBoxDragFilter, self).__init__(*args, **kwargs)
        self._dragSensitivity = 5  # pixels per step
        self._startSensitivity = 10  # pixel move to start the dragging
        # private vars
        self._lastPos = QtCore.QPoint()
        self._leftover = 0
        self._dragStart = None
        self._firstDrag = False
        self._dragType = self.DRAG_NONE

    def eventFilter(self, cls, e):
        if e.type() == QtCore.QEvent.MouseButtonPress:
            if e.button() & QtCore.Qt.RightButton:
                cls.setValue(self.defaultValue)
                return True

        elif e.type() == QtCore.QEvent.ContextMenu:
            return True  # Kill the context menu

        elif e.type() == QtCore.QEvent.MouseMove:
            stepHolder = cls.singleStep()
            print self._dragType
            if self._dragType:
                if self._dragType == self.DRAG_HORIZONTAL:
                    delta = e.pos().x() - self._lastPos.x()
                else:
                    delta = self._lastPos.y() - e.pos().y()

                self._leftover += delta
                self._lastPos = e.pos()

                cls.stepBy(int(self._leftover / self._dragSensitivity))
                self._leftover %= self._dragSensitivity

            else:
                if e.buttons() & QtCore.Qt.LeftButton:  # only allow left-click dragging
                    if self._dragStart is None:
                        self._dragStart = e.pos()

                    if abs(e.x() - self._dragStart.x()) > self._startSensitivity:
                        self._dragType = self.DRAG_HORIZONTAL
                    if abs(e.y() - self._dragStart.y()) > self._startSensitivity:
                        self._dragType = self.DRAG_VERTICAL

            cls.setSingleStep(stepHolder)


        elif e.type() == QtCore.QEvent.MouseButtonRelease:
            # Only reset the dragType if it's *not* the first drag event release
            if self._firstDrag:
                self._firstDrag = False
            elif self._dragType:
                self._dragType = self.DRAG_NONE
                self._lastPos = QtCore.QPoint()
                self._dragStart = None

        return cls.eventFilter(cls, e)
