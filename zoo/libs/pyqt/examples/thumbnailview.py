import os
from functools import partial

from qt import QtWidgets, QtCore
from zoo.libs.pyqt.extended.imageview import model, items, thumbwidget
from zoo.libs.utils import file


class ExampleThumbnailViewerModel(model.ItemModel):
    """Overridden base model to handle custom loading of the data eg. files
    """

    def __init__(self, view, directory=""):
        super(ExampleThumbnailViewerModel, self).__init__(parent=view)
        self.view = view
        self.directory = directory
        self.currentFilesList = []
        self.threadpool = QtCore.QThreadPool()

    def onDirectoryChanged(self, directory):
        # honestly this first stage should be done in the view and on a separate thread
        self.items = []
        self.loadedCount = 0
        self.directory = directory
        self.currentFilesList = []
        self.clear()
        self.listFiles()
        self.loadData()

    def listFiles(self):
        """Simple functions which gathers all the images to load upfront, probably could do this on a thread and in
        chunks
        """
        results = []
        for i in os.listdir(self.directory):
            path = os.path.join(self.directory, i)
            if file.isImage(path):
                results.append(path)
        self.currentFilesList = results

    def createItem(self, item):
        tItem = items.TreeItem(item=item)
        self.items.append(tItem)
        self.appendRow(tItem)
        return tItem

    def loadData(self):
        """Overridden to prep the images from load and viewing in the view, you can do anything in here.
        Lazy loading happens either on first class initiization and any time the vertical bar hits the max value, we than
        grab the current the new file chunk by files[self.loadedCount: loadedCount + self.chunkCount] that way we are
        only loading a small amount at a time.
        Since this is an example of how to use the method , you can approach it in any way you wish but for each item you
        add you must initialize a item.BaseItem() or custom subclass and a item.treeItem or subclass which handles the
        qt side of the data per item

        """
        if len(self.currentFilesList) < self.loadedCount:
            filesToLoad = self.currentFilesList
        else:
            filesToLoad = self.currentFilesList[self.loadedCount: self.loadedCount + self.chunkCount]
        for f in filesToLoad:
            workerThread = items.ThreadedIcon(iconPath=f)
            # create an item for the image type
            it = items.BaseItem(name=os.path.basename(f).split(os.extsep)[0], iconPath=f)
            qitem = self.createItem(item=it)
            workerThread.signals.updated.connect(partial(self.setItemIconFromImage, qitem))
            self.threadpool.start(workerThread)
        self.reset()

    def setItemIconFromImage(self, item, image):
        item.applyFromImage(image)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    wid = thumbwidget.ThumbnailViewWidget()
    rootDirectory = r"D:\\reference"
    model = ExampleThumbnailViewerModel(wid, rootDirectory)
    # set a custom chunk count
    # model.chunkCount = 50
    wid.setModel(model)
    model.listFiles()
    model.loadData()
    wid.show()
    # set the icon size
    wid.setIconSize(QtCore.QSize(1024,1024))
    # set the min/max icon size, takes a int instead of a width height since images are rescaled to main aspect ratio
    wid.setIconMinMax((64, 512))
    sys.exit(app.exec_())
