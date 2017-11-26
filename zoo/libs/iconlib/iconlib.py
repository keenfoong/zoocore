import os

from qt import QtGui, QtCore
from zoo.libs.maya.utils import env


class Icon(object):
    """This class acts as a uniform interface to manipulate, create, retrieve Qt icons from the zoo library.
    """
    iconCollection = {}
    iconPaths = []
    if not iconCollection:
        # find and store all the found icons with the base zoo paths
        iconPaths = os.environ["ZOO_ICON_PATH"].split(os.pathsep)
        for iconPath in iconPaths:
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
                    if name in iconCollection:
                        sizes = iconCollection[name]["sizes"]
                        if size in sizes:
                            continue
                        sizes[size] = {"path": os.path.join(root, f),
                                       "icon": None}

                    else:
                        iconCollection[name] = {"sizes": {size: {"path": os.path.join(root, f),
                                                                 'icon': None}},
                                                "name": name}

    @classmethod
    def icon(cls, iconName, size=16):
        """Returns a QtGui.QIcon instance intialized to the icon path for the icon name if the icon name is found within
        the cache

        :param iconName: str, iconName_size or iconName, if not size in name then 16px will be used
        :param size: int, the size of the icon, the size will be used for both the width and height
        :return: QtGui.Qicon
        """
        if env.isMayapy():
            return

        if "_" in iconName:
            splitter = iconName.split("_")
            if splitter[-1].isdigit():
                iconName = "_".join(splitter[:-1])
                # user requested the size in the name
                size = splitter[-1]
        else:
            size = str(size)
        if iconName not in cls.iconCollection:
            return QtGui.QIcon()

        for name, data in iter(cls.iconCollection.items()):
            if name != iconName:
                continue
            sizes = data["sizes"]
            if size not in sizes:
                size = sizes.keys()[0]
                iconData = sizes[size]
            else:
                iconData = data["sizes"][size]
            icondata = iconData["icon"]
            if icondata and isinstance(icondata, QtGui.QIcon) and not icondata.isNull():
                return icondata
            newIcon = QtGui.QIcon(iconData["path"])
            data["sizes"][size]["icon"] = newIcon
            return newIcon

        return QtGui.QIcon()

    @classmethod
    def iconColorized(cls, iconName, size=16, color=(255, 255, 255)):
        """Colorizers the icon from the library expects the default icon
        to be white for tinting.

        :param iconName: the icon name from the library
        :type iconName: str
        :param size: the uniform icon size
        :type size: int
        :param color: 3 tuple for the icon color
        :type color: tuple(int)
        :return: the colorized icon
        :rtype: QtGui.QIcon
        """
        icon = cls.icon(iconName, size)
        if not icon:
            return icon  # will return an empty QIcon
        color = QtGui.QColor(*color)

        pixmap = icon.pixmap(QtCore.QSize(size, size))
        mask = pixmap.createMaskFromColor(QtGui.QColor('white'), QtCore.Qt.MaskOutColor)
        pixmap.fill(color)
        pixmap.setMask(mask)
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