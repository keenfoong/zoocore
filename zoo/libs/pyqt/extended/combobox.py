from qt import QtWidgets, QtCore


class ExtendedComboBox(QtWidgets.QComboBox):
    """Extended combobox to also have a filter
    """

    def __init__(self, items=None, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setEditable(True)
        self._isCheckable = False

        # add a filter model to filter matching items
        self.pFilterModel = QtCore.QSortFilterProxyModel(self, filterCaseSensitivity=QtCore.Qt.CaseInsensitive)

        self.complete = QtWidgets.QCompleter(self)
        self.complete.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        # bug thats been around for at 3 years where in pyside you need to set the completer model like this instead
        # of passing into the init lol
        self.complete.setModel(self.pFilterModel)
        self.setCompleter(self.complete)
        self.pFilterModel.setSourceModel(self.model())

        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.complete.activated.connect(self.onCompleterActivated)
        if items:
            self.addItems(items)

    def addItem(self, text, isCheckable=False):
        super(ExtendedComboBox, self).addItem(text)
        model = self.model()
        item = model.item(model.rowCount() - 1, 0)
        if item and isCheckable:
            self._isCheckable = isCheckable
            item.setCheckState(QtCore.Qt.Checked)

    def onCompleterActivated(self, text):
        """On selection of an item from the completer, this method will select the item from the combobox
        """
        # on selection of an item from the completer, select the corresponding item from combobox
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated.emit(str(self.itemText(index)))

    def setModel(self, model):
        """Overridden to set the filter and completer models
        """
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.complete.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        # on model column change, update the model column of the filter and completer as well
        self.complete.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)

    def handleItemPressed(self, index):
        if not self._isCheckable:
            return
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            state = QtCore.Qt.Unchecked
        else:
            state = QtCore.Qt.Checked
        item.setCheckState(state)
        self.checkStateChanged.emit(item.text(), state)

    def stateList(self):
        model = self.model()
        items = []
        for index in range(model.rowCount()):
            item = model.itemFromIndex(index)
            if item.isValid():
                items.append(item)
        return items

    def checkedItems(self):
        model = self.model()
        items = []
        for index in range(model.rowCount()):
            item = model.itemFromIndex(index)
            if item.isValid():
                items.append(item)
        return items
