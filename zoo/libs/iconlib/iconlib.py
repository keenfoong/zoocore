# @todo icon colours
# @todo icon resizing

import os
from zoo.libs.pyqt.qt import QtGui
from zoo.libs.maya.utils import general


class Icon(object):
    """This class acts as a uniform interface to manipulate, create, retrieve Qt icons from the zoo library.
    """
    iconCollection = {}
    iconPaths = []
    if not iconCollection:
        # find and store all the found icons with the base zoo paths
        iconPaths = os.environ["ZOO_ICON_PATH"].split(os.pathsep)
        for iconPath in iconPaths:
            if not iconPath:
                continue
            for root, dirs, files in os.walk(iconPath):
                for f in files:
                    fname = f.split(os.extsep)[0]
                    nameSplit = fname.split("_")
                    name = "_".join(nameSplit[:-1])
                    size = nameSplit[-1]
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
        if general.isMayapy():
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
            if size not in data["sizes"]:
                return QtGui.QIcon()
            iconData = data["sizes"][size]
            icon = iconData["icon"]
            if icon and isinstance(iconData["icon"], QtGui.QIcon) and not icon.isNull():
                return icon
            newIcon = QtGui.QIcon(iconData["path"])
            data["sizes"][size]["icon"] = newIcon
            return newIcon

        return QtGui.QIcon()
