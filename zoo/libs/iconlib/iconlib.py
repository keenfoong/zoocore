import os

from qt import QtGui, QtCore
from zoo.libs.utils import env


class Icon(object):
    """This class acts as a uniform interface to manipulate, create, retrieve Qt icons from the zoo library.
    """
    iconCollection = {}
    iconPaths = []

    @classmethod
    def reload(cls):
        cls.iconCollection = {}

        # find and store all the found icons with the base zoo paths
        cls.iconPaths = os.environ.get("ZOO_ICON_PATH", "").split(os.pathsep)
        for iconPath in cls.iconPaths:
            if not iconPath or not os.path.exists(iconPath):
                continue
            for root, dirs, files in os.walk(iconPath):
                for f in files:
                    if not f.endswith(".png"):
                        continue
                    fname = f.split(os.extsep)[0]
                    nameSplit = fname.split("_")
                    if len(nameSplit) < 1:
                        continue
                    name = "_".join(nameSplit[:-1])
                    size = int(nameSplit[-1])
                    if name in cls.iconCollection:
                        sizes = cls.iconCollection[name]["sizes"]
                        if size in sizes:
                            continue
                        sizes[size] = {"path": os.path.join(root, f),
                                       "icon": None}

                    else:
                        cls.iconCollection[name] = {"sizes": {size: {"path": os.path.join(root, f),
                                                                     'icon': None}},
                                                    "name": name}

    @classmethod
    def icon(cls, iconName, size=16):
        """Returns a QtGui.QIcon instance intialized to the icon path for the icon name if the icon name is found within
        the cache

        :param iconName: str, iconName_size or iconName, then it will resize the largest icon found
        :param size: int, the size of the icon, the size will be used for both the width and height.
                     setting size=-1 will return the largest icon as well
        :return: QtGui.Qicon
        """
        if env.isMayapy():
            return
        iconData = cls.iconDataForName(iconName, size)
        icon = iconData.get("icon")
        if icon and isinstance(icon, QtGui.QIcon) and not icon.isNull():
            if size != -1:
                icon = cls.resizeIcon(icon, QtCore.QSize(size, size))
            return icon

        newIcon = QtGui.QIcon(iconData.get("path", ""))
        iconData["icon"] = newIcon
        return newIcon

    @classmethod
    def resizeIcon(cls, icon, size):
        """
        Resizes the icon. Defaults to smooth bilinear scaling and keep aspect ratio.
        :param icon: Icon to resize
        :param size: New size to scale to
        :type size: QtCore.QSize
        :return:
        """
        if len(icon.availableSizes()) == 0:
            return

        origSize = icon.availableSizes()[0]
        pixmap = icon.pixmap(origSize)
        pixmap = pixmap.scaled(size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        return QtGui.QIcon(pixmap)

    @classmethod
    def iconDataForName(cls, iconName, size=16):

        if "_" in iconName:
            splitter = iconName.split("_")
            if splitter[-1].isdigit():
                iconName = "_".join(splitter[:-1])
                # user requested the size in the name
                size = splitter[-1]
        else:
            size = str(size)
        if iconName not in cls.iconCollection:
            return {}

        for name, data in iter(cls.iconCollection.items()):
            if name != iconName:
                continue
            sizes = data["sizes"]

            if size not in sizes:
                size = sizes.keys()[-1]
                iconData = sizes[size]
            else:
                iconData = data["sizes"][size]
            return iconData
        return {}

    @classmethod
    def iconPathForName(cls, iconName, size=16):
        return cls.iconDataForName(iconName, size).get("path", "")

    @classmethod
    def iconColorized(cls, iconName, size=16, color=(255, 255, 255), overlayName=None, overlayColor=(255,255,255)):
        """Colorizes the icon from the library expects the default icon
        to be white for tinting.

        :param iconName: the icon name from the library
        :type iconName: str
        :param size: the uniform icon size
        :type size: int
        :param color: 3 tuple for the icon color
        :type color: tuple(int)
        :return: the colorized icon
        :param overlayName: The name of the icon that will be overlayed on top of the original icon
        :param overlayColor: The colour of the overlay
        :rtype: QtGui.QIcon
        """
        iconLargest = cls.icon(iconName, -1)

        if not iconLargest:
            return iconLargest  # will return an empty QIcon

        origSize = iconLargest.availableSizes()[0]
        pixmap = cls.colorPixmap(iconLargest.pixmap(origSize), color)

        if overlayName is not None:
            overlayIcon = cls.icon(overlayName, -1)
            overlayPixmap = overlayIcon.pixmap(origSize)
            cls.addOverlay(pixmap, overlayPixmap, overlayColor)

        pixmap = pixmap.scaled(QtCore.QSize(size, size), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        return QtGui.QIcon(pixmap)

    @classmethod
    def grayscaleIcon(cls, iconName, size):
        """ Returns a grayscale version of a given icon. Returns the original icon
        if it cannot be converted.
        :param iconName: The icon name from the library
        :type iconName: str
        :param size: the size of the icon to retrieve
        :type size: int
        :rtype: QtGui.QIcon
        """
        icon = cls.icon(iconName, size)
        if not icon:
            return icon  # will return an empty QIcon
        # Rebuild all sizes of the icon as grayscale
        for size in icon.availableSizes():
            icon.addPixmap(icon.pixmap(size, QtGui.QIcon.Disabled))
        return icon

    @classmethod
    def colorPixmap(cls, pixmap, color):
        """
        Colorize the pixmap with a new color based on its alpha map
        :param pixmap: Pixmap
        :type pixmap: QtGui.QPixmap
        :param color: new color in tuple format (255,255,255)
        :return:
        """
        color = QtGui.QColor(*color)
        mask = pixmap.mask()
        pixmap.fill(color)
        pixmap.setMask(mask)

        return pixmap

    @classmethod
    def addOverlay(cls, pixmap, overlayPixmap, color):
        """
        Overlays one pixmap over the other
        :param pixmap: The source pixmap
        :type pixmap: QtGui.QPixmap
        :param overlayPixmap: the pixmap to overlay on top of the source pixmap
        :type overlayPixmap: QtGui.QPixmap
        :param color: The colour of the overlay pixmap
        :type color: tuple(int,int,int)
        :return:
        """

        # Set the color for the overlay
        overlayPixmap = cls.colorPixmap(overlayPixmap, color)

        # Paint the overlay pixmap over the original
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, overlayPixmap.width(), overlayPixmap.height(), overlayPixmap)
        painter.end()

Icon.reload()

