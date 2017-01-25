import os

from maya import cmds
from maya.OpenMaya import MGlobal
from zoo.libs.utils import zlogging
from zoo.libs.maya.utils import env

logger = zlogging.zooLogger


def mayaUpVector():
    """Gets the current world up vector

    :rtype: zoo.libs.utils.vectors.Vector
    """
    return MGlobal.upAxis()


def isYAxisUp():
    """returns True if y is world up

    :return: bool
    """
    return MGlobal.isYAxisUp()


def isZAxisUp():
    """returns True if Z is world up

    :return: bool
    """
    return MGlobal.isZAxisUp()


def isXAxisUp():
    """returns True if x is world up

    :return: bool
    """
    return True if not isYAxisUp() and not isZAxisUp() else False


def loadPlugin(pluginPath):
    try:
        if not isPluginLoaded(pluginPath):
            cmds.loadPlugin(pluginPath)
    except RuntimeError:
        logger.debug("Could not load plugin->{}".format(pluginPath))


def unloadPlugin(pluginPath):
    try:
        if isPluginLoaded(pluginPath):
            cmds.unloadPlugin(pluginPath)
    except RuntimeError:
        logger.debug("Could not load plugin->{}".format(pluginPath))


def isPluginLoaded(pluginPath):
    return cmds.pluginInfo(pluginPath, q=True, loaded=True)


def getMayaPlugins():
    location = env.getMayaLocation(env.mayaVersion())
    plugins = set()
    for path in [i for i in env.mayaPluginPaths() if i.startswith(location) and os.path.isdir(i)]:
        for x in os.listdir(path):
            if os.path.isfile(os.path.join(path, x)) and isPluginLoaded(path):
                plugins.add(x)
    return list(plugins)


def loadAllMayaPlugins():
    logger.debug("loading All plugins")
    for plugin in getMayaPlugins():
        loadPlugin(plugin)
    logger.debug("loaded all plugins")


def unLoadMayaPlugins():
    logger.debug("unloading All plugins")
    for plugin in getMayaPlugins():
        unloadPlugin(plugin)
    logger.debug("unloaded all plugins")
