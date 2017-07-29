# @todo split the env out to a config file (JSON) for cleaner code and better integration
import os
import sys
import site

from zoo.libs.utils import filesystem
from zoo.libs.utils import zlogging
from zoo.libs.utils import env

logger = zlogging.zooLogger


def _initEnv():
    """Initialize's the zoo plugin environment, this does create a few environment variables.
       We allow for the user to extend these variables with os.pathsep.
       Env vars:
       ZOO_BASE, ZOO_ICON_PATH, ZOO_DEBUG_LOGGING
    """
    logger.debug("initializing zoo environment")
    # setup standard envs
    zootoolsPath = str(filesystem.upDirectory(__file__, 3))
    pPaths = ""
    if "PYTHONPATH" in os.environ:
        pPaths = os.environ["PYTHONPATH"].split(os.pathsep)

    if zootoolsPath not in pPaths:
        logger.debug("Adding path -> {} to sys.path".format(zootoolsPath))
        sys.path.append(zootoolsPath)
    # deal with the zoo base directory
    basePaths = os.environ.get("ZOO_BASE", "")
    iconPath = os.environ.get("ZOO_ICON_PATH", None)
    if not basePaths:
        logger.debug("setting up ZOO_BASE env -> {}".format(zootoolsPath))
        os.environ["ZOO_BASE"] = str(zootoolsPath) + os.pathsep
    elif zootoolsPath not in basePaths:
        logger.debug("Adding env -> {} to current ZOO_BASE, existing -> {}".format(zootoolsPath,
                                                                                   os.environ["ZOO_BASE"]))
        os.environ["ZOO_BASE"] = zootoolsPath + os.pathsep + basePaths
    if not iconPath:
        logger.debug("setting up ZOO_ICON_PATH env -> {}".format(os.path.join(zootoolsPath, "icons")))
        os.environ["ZOO_ICON_PATH"] = os.path.join(zootoolsPath, "icons") + os.pathsep
    elif os.path.join(zootoolsPath, "icons") not in iconPath:
        logger.debug("Adding env -> {} to current ZOO_ICON_PATH, existing -> {}".format(os.path.join(zootoolsPath,
                                                                                                     "icons"),
                                                                                        os.environ["ZOO_ICON_PATH"]))
        os.environ["ZOO_ICON_PATH"] += os.path.join(zootoolsPath, "icons") + os.pathsep
    metapaths = os.environ.get("ZOO_META_PATHS", "")
    basemeta = os.path.join(zootoolsPath, "zoo", "libs", "maya", "meta", "base")
    metarig = os.path.join(zootoolsPath, "zoo", "libs", "maya", "rig", "metarig")
    if not metapaths:
        os.environ["ZOO_META_PATHS"] = basemeta + os.pathsep + metarig + os.pathsep
    elif basemeta not in metapaths:
        os.environ["ZOO_META_PATHS"] += basemeta + os.pathsep
    if metarig not in metapaths:
        os.environ["ZOO_META_PATHS"] += metarig + os.pathsep
    site.addsitedir(os.path.realpath(os.path.join(zootoolsPath, "thirdparty")))

    if "ZOO_LOG_LEVEL" not in os.environ:
        os.environ['ZOO_LOG_LEVEL'] = 'DEBUG'
    # register commands
    from zoo.libs.command import executor
    mayalib = os.path.join(zootoolsPath, "zoo", "libs", "maya", "mayacommand", "library")
    os.environ["ZOO_COMMAND_LIB"] = os.pathsep.join([os.path.join(zootoolsPath, "zoo", "libs", "command", "library"), mayalib])
    executor.Executor().registerEnv("ZOO_COMMAND_LIB")


def _setupMaya():
    from zoo.libs.maya import mayastartup
    logger.debug("Starting up zoo maya")
    mayastartup.ZooMayaStartUp()


def startUp():
    _initEnv()
    if env.isInMaya():
        _setupMaya()
