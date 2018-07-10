"""
root
    |-hotkeys
    |-tools
        |- toolName
                |-settingOne.json
                |SettingTwoFolder
                            |-setting.json


"""
import os
import logging
import copy
from collections import OrderedDict

from zoo.libs.utils import filesystem
from zoo.libs.utils import file, path

logger = logging.getLogger(__name__)


class RootAlreadyExistsError(Exception):
    pass


class RootDoesntExistsError(Exception):
    pass


class InvalidSettingsPath(Exception):
    pass


class InvalidRootError(Exception):
    pass


class ToolSet(object):
    """
    Example::
        Create some roots
        >>> tset = ToolSet()
        # the order you add roots is important
        >>> tset.addRoot(os.path.expanduser("~/Documents/maya/2018/scripts/zootools_preferences"), "userPreferences")
        # create a settings instance, if one exists already within one of the roots that setting will be used unless you
        # specify the root to use, in which the associated settingsObject for the root will be returned
        >>> newSetting = tset.createSetting(relative="tools/tests/helloworld",
        ...                                root="userPreferences",
        ...                                data={"someData": "hello"})
        >>> print os.path.exists(newSetting.path())
        >>> print newSetting.path()
        # lets open a setting
        >>> foundSetting = tset.findSetting(relative="tools/tests/helloworld", root="userPreferences")

    """

    def __init__(self):
        self.roots = OrderedDict()
        self.extension = ".json"
    def root(self, name):
        if name not in self.roots:
            raise RootDoesntExistsError("Root by the name: {} doesn't exist".format(name))
        return self.roots[name]

    def addRoot(self, fullPath, name):
        if name in self.roots:
            raise RootAlreadyExistsError("Root already exists: {}".format(name))
        self.roots[name] = path.Path(fullPath)

    def findSetting(self, relativePath, root=None, extension=None):
        """ finds a settings object by searching the roots in reverse order.

        The first path to exist will be the one to be resolved. If a root is specified
        and the root+relativePath exists then that will be returned instead

        :param relativePath:
        :type relativePath: str
        :param root: The Root name to search if root is None then all roots in reverse order will be search until a
        settings is found.
        :type root: str or None
        :return:
        :rtype: ::class:`SettingObject`
        """
        relativePath = path.Path(relativePath)
        if not relativePath.getExtension(True):
            relativePath = relativePath.setExtension(extension or self.extension)

        if root is not None:
            rootPath = self.roots.get(root)
            if rootPath is not None:
                fullpath = rootPath / relativePath
                if not fullpath.exists():
                    return SettingObject(rootPath, relativePath)
                return self.open(rootPath, relativePath)
        else:
            for name, p in reversed(self.roots.items()):
                # we're working with an ordered dict
                fullpath = p / relativePath
                if not fullpath.exists():
                    continue
                return self.open(p, relativePath)

        return SettingObject("", relativePath)

    def settingFromRootPath(self, relativePath, rootPath):
        fullpath = rootPath / relativePath
        if not fullpath.exists():
            return self.open(rootPath, relativePath)
        return SettingObject("", relativePath)

    def createSetting(self, relative, root, data):
        setting = self.findSetting(relative, root)
        setting.update(data)
        return setting

    def open(self, root, relativePath, extension=None):
        relativePath = path.Path(relativePath)
        if not relativePath.getExtension(True):
            relativePath = relativePath.setExtension(extension or self.extension)
        fullPath = root / relativePath
        if not os.path.exists(fullPath):
            raise InvalidSettingsPath(fullPath)
        data = file.loadJson(fullPath)
        return SettingObject(root, relativePath, **data)


class SettingObject(dict):
    """Settings class to encapsulate the json data for a given setting
    """

    def __init__(self, root, relativePath=None, **kwargs):

        relativePath = path.Path(relativePath or "")
        if not relativePath.getExtension(True):
            relativePath = relativePath.setExtension(".json")
        kwargs["relativePath"] = relativePath
        kwargs["root"] = root
        super(SettingObject, self).__init__(**kwargs)

    def rootPath(self):
        if self.root:
            return self.root
        return path.Path()

    def path(self):
        return self.root / self["relativePath"]

    def isValid(self):
        if self.root is None:
            return False
        elif (self.root / self.relativePath).exists():
            return True
        return False

    def __repr__(self):
        return "<{}> root: {}, path: {}".format(self.__class__.__name__, self.root, self.relativePath)

    def __cmp__(self, other):
        return self.name == other and self.version == other.version

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return super(SettingObject, self).__getattribute__(item)

    def __setattr__(self, key, value):
        self[key] = value

    def save(self):
        root = self.root

        if not root:
            return path.Path()
        fullPath = root / self.relativePath
        filesystem.ensureFolderExists(os.path.dirname(str(fullPath)))
        output = copy.deepcopy(self)
        del output["root"]
        del output["relativePath"]
        exts = fullPath.getExtension(True)
        if not exts:
            fullPath = fullPath.setExtension("json", True)
        file.saveJson(output, str(fullPath))
        return self.path()
