import os
from qt import QtWidgets
from zoo.libs.pyqt.extended.imageview import model, item, listview


class ExampleThumbnailViewerModel(model.ItemModel):
    def __init__(self, view, directory=""):
        super(ExampleThumbnailViewerModel, self).__init__()
        self.view = view
        self.directory = directory
        self.currentFilesList = []
        self.listFiles()
        self.loadData()

    def onDirectoryChanged(self, directory):
        self.clear()
        self.directory = directory
        self.listFiles()
        self.loadData()

    def listFiles(self):
        self.currentFilesList = [os.path.join(self.directory, i) for i in os.listdir(self.directory)]

    def loadData(self):
        if len(self.currentFilesList) < self.loadedCount:
            filesToLoad = self.currentFilesList
        else:
            filesToLoad = self.currentFilesList[self.loadedCount: self.loadedCount + self._chunkCount]
        for f in filesToLoad:
            it = item.Item()
            it.iconPath = f
            tItem = item.TreeItem(it)
            self.items.append(tItem)
            self.appendRow(tItem)
            self.loadedCount += 1
        self.reset()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    wid = listview.ExtendedItemView()
    wid.setModel(ExampleThumbnailViewerModel(wid, r"C:\\"))
    wid.show()
    sys.exit(app.exec_())
