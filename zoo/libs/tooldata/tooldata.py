import os
import logging

from zoo.libs.utils import filesystem
from zoo.libs.utils import path as pathutils
from zoo.libs.utils import file

logger = logging.getLogger(__name__)

ROOT_LOCATION_ENV = "ZOO_TOOLDATA_ROOT"


def getRoot():
    """Returns the root path of the tool data files

    :return: the environment variable path
    :rtype: str
    """
    return os.environ.get(ROOT_LOCATION_ENV, "")


def findTools(root):
    tools = {}
    for i in os.listdir(root):
        t = Tool(os.path.normpath(os.path.join(root, i)))
        tools[i] = t
    return tools


class ToolSet(object):
    def __init__(self, root):
        self.root = root
        self.tools = {}
        self.populate()

    def hasTool(self, toolName):
        """

        :param toolName:
        :type toolName: str
        :return:
        :rtype: bool
        """
        return toolName in self.tools

    def populate(self):
        self.tools = findTools(self.root)

    def find(self, toolName):
        """

        :param toolName:
        :type toolName: str
        :return:
        :rtype: `Tool`
        """
        if not self.tools:
            self.populate()
        if toolName not in self.tools:
            t = Tool()
            t.name = toolName
            return t
        return self.tools[toolName]

    def createTool(self, tool):
        if tool.name in self.tools:
            raise ValueError("Tool already exists")
        path = os.path.join(self.root, tool.name)
        filesystem.ensureFolderExists(path)
        to = Tool(path)
        self.tools[tool.name] = to
        return to


class Tool(object):
    def __init__(self, path=None):
        self.path = path or ""
        self.name = ""
        self.settings = {}

        if os.path.exists(self.path):
            self.name = os.path.basename(self.path)
            self.settings = dict.fromkeys(os.listdir(self.path), {})
        self.gather()

    def isValid(self):
        return os.path.exists(self.path)

    def get(self, category, version=-1, *paths):
        settings = self.settings.get(category)
        if not settings:
            return SettingObject(None, relativePath="|".join(paths), version=1, category=category, name=paths[-1])
        if version == -1:
            version = max([int(i.split("|")[-1]) for i in settings.keys()])
        relativePath = "|".join(list(paths) + [str(version).zfill(3)])
        f = settings.get(relativePath)
        if f:
            return SettingObject(f, relativePath=relativePath, category=category)

    def gather(self):
        for g in self.settings.keys():
            path = os.path.join(self.path, g)
            files = {}
            for i in self._parse(filesystem.directoryTreeToDict(path)):
                settingsPath = i["path"]
                versionNumberStr = pathutils.getVersionNumberAsStr(settingsPath)
                relativePath = pathutils.Path(settingsPath).relativeTo(path).removeExtensions()
                relativePath = str(relativePath).replace("_v" + versionNumberStr, "|" + versionNumberStr)

                files[relativePath.replace("/", "|")] = settingsPath
            self.settings[g] = files

    def _parse(self, dep):
        for i in dep.get("children", []):
            if i["type"] == "file":
                yield i
            for t in self._parse(i):
                yield t

    def latestFromSetting(self, setting):
        sets = self.settings[setting.category]
        versions = [int(i.split("|")[-1]) for i in sets.keys()]
        version = max(versions)
        setter = sets[sets.keys()[versions.index(version)]]
        return SettingObject(setter, relativePath=setting.relativePath, category=setting.category)

    def saveNewSetting(self, setting):
        """

        :param setting:
        :type setting: SettingObject
        :return:
        :rtype: SettingObject
        """
        categoryPath = os.path.join(self.path, setting.category)

        paths = setting.relativePath.split("|")
        fileName = paths[-1] + "_v001.json"
        if len(paths) > 1:
            fullPath = os.path.join(*tuple([categoryPath] + paths[:-1] + [fileName]))
        else:
            fullPath = os.path.join(categoryPath, fileName)
        if not os.path.exists(categoryPath):
            filesystem.ensure_folder_exists(os.path.dirname(fullPath))
        relativePath = "|".join(paths + ["001"])
        setting["relativePath"] = relativePath
        file.saveJson(dict(setting), fullPath)
        setting["filePath"] = fullPath
        return setting

    def saveNewVersion(self, setting):
        latestSetting = self.latestFromSetting(setting)
        nextVersion = latestSetting.version + 1
        newSetting = SettingObject(**setting)
        newSetting.version = nextVersion
        newVersionStr = str(nextVersion).zfill(3)
        currentRelativePath = setting.relativePath.split("|")
        newSetting.relativePath = "|".join(currentRelativePath[:-1] + [newVersionStr])

        newPath = newSetting.filePath.replace("_v" + pathutils.getVersionNumberAsStr(os.path.basename(newSetting.filePath)),
            "_v{}".format(newVersionStr))
        del newSetting["filePath"]
        file.saveJson(dict(newSetting), newPath)
        return newSetting


class SettingObject(dict):
    def __init__(self, filePath=None, relativePath=None, **kwargs):
        try:
            if filePath:
                kwargs.update(file.loadJson(filePath))
            kwargs["relativePath"] = relativePath or ""
            kwargs["filePath"] = filePath or ""
            super(SettingObject, self).__init__(**kwargs)
        except TypeError:
            raise ValueError("Invalid json file {}".format(filePath))

    def isValid(self):
        return os.path.exists(self.filePath)

    def __repr__(self):
        return "<{}> name: {}, version: {}".format(self.__class__.__name__, self.name, self.version)

    def __cmp__(self, other):
        return self.name == other and self.version == other.version

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return super(SettingObject, self).__getattribute__(item)

    def __setattr__(self, key, value):
        self[key] = value