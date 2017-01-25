import logging
import os
import sys

from tests import unittestBase
from maya import cmds
from zoo import startup
logger = logging.getLogger(__name__)


class BaseMayaTest(unittestBase.BaseUnitest):
    """Base class for all maya based unitests, provides helper methods for loading and loading plugins
    """
    loadedPlugins = set()
    application = "maya"

    @classmethod
    def loadPlugin(cls, pluginName):
        """Loads a given plugin and stores it on the class
        :param pluginName: str, the plugin to load
        """
        cmds.loadPlugin(pluginName)
        logger.debug("Loaded Plugin %s" % pluginName)
        cls.loadedPlugins.add(pluginName)

    @classmethod
    def unloadPlugins(cls):
        """Unload all the currently loaded plugins
        """
        for plugin in cls.loadedPlugins:
            cmds.unloadPlugin(plugin)
            logger.debug("unLoaded Plugin %s" % plugin)
        cls.loadedPlugins.clear()

    def tearDown(self):
        cmds.file(f=True, new=True)

    @classmethod
    def tearDownClass(cls):
        """Calls on cls.unloadPlugins()
        """
        super(BaseMayaTest, cls).tearDownClass()
        cls.unloadPlugins()


def commandline():
    from maya import standalone
    standalone.initialize()
    realsyspath = [os.path.realpath(p) for p in sys.path]
    pythonpath = os.environ.get('PYTHONPATH', '')
    for p in pythonpath.split(os.pathsep):
        p = os.path.realpath(p)
        if p not in realsyspath:
            sys.path.insert(0, p)
    testSuites = unittestBase.getTests()
    startup.startUp()
    if "maya" in testSuites:
        unittestBase.runTests(testSuites["maya"])

    standalone.uninitialize()
    os._exit(0) # to fix seg fault in maya 2017 because autodesk is stupid

if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    commandline()