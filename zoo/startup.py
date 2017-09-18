# @todo split the env out to a config file (JSON) for cleaner code and better integration
import os
import sys
import site

from zoo.libs.utils import filesystem
from zoo.libs.utils import zlogging
from zoo.libs.utils import env
from zoo.libs.command import executor

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
    env.addToEnv("ZOO_BASE", (zootoolsPath, ))
    env.addToEnv("ZOO_ICON_PATH", (os.path.join(zootoolsPath, "icons"), ))

    site.addsitedir(os.path.realpath(os.path.join(zootoolsPath, "thirdparty")))

    if "ZOO_LOG_LEVEL" not in os.environ:
        os.environ['ZOO_LOG_LEVEL'] = 'DEBUG'


def _setupMaya():
    from zoo.libs.maya import mayastartup
    logger.debug("Starting up zoo maya")
    mayastartup.ZooMayaStartUp()

    # register commands
    zootoolsPath = str(filesystem.upDirectory(__file__, 3))
    mayalib = os.path.join(zootoolsPath, "zoo", "libs", "maya", "mayacommand", "library")
    basemeta = os.path.join(zootoolsPath, "zoo", "libs", "maya", "meta", "base.py")
    metacamera = os.path.join(zootoolsPath, "zoo", "libs", "maya", "meta", "metacamera.py")
    metarig = os.path.join(zootoolsPath, "zoo", "libs", "maya", "rig", "metarig.py")
    env.addToEnv("ZOO_META_PATHS", (basemeta, metarig, metacamera))
    env.addToEnv("ZOO_COMMAND_LIB", (os.path.join(zootoolsPath, "zoo", "libs", "command", "library"), mayalib))
    executor.Executor().registerEnv("ZOO_COMMAND_LIB")


def startUp():
    _initEnv()
    if env.isInMaya():
        _setupMaya()
