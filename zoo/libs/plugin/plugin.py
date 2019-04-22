import inspect
import time
from zoo.libs.utils import env


class Plugin(object):
    """Base plugin class that all plugins inherent from. The client should subclass this to provide a standard
    interface when needed.

    .. code-block:: python

        Class CustomPlugin(Plugin):
            id = "CustomPlugin.example"
            def execute(self):
                print "executed plugin: {}".format(self.id)

    """
    id = ""

    def __init__(self, manager=None):
        self.manager = manager
        self.stats = PluginStats(self)


class PluginStats(object):
    def __init__(self, plugin):
        self.plugin = plugin
        self.id = self.plugin.id
        self.startTime = 0.0
        self.endTime = 0.0
        self.executionTime = 0.0

        self.info = {}
        self._init()

    def _init(self):
        """Initializes some basic info about the plugin and the use environment
        Internal use only.
        """
        self.info.update({"name": self.plugin.__class__.__name__,
                          "creator": self.plugin.creator,
                          "module": self.plugin.__class__.__module__,
                          "filepath": inspect.getfile(self.plugin.__class__),
                          "id": self.id,
                          "application": env.application()
                          })
        self.info.update(env.machineInfo())

    def start(self):
        self.startTime = time.time()

    def finish(self, tb=None):
        """Called when the plugin has finish executing.

        :param tb:
        :type tb:
        """
        self.endTime = time.time()
        self.executionTime = self.endTime - self.startTime
        self.info["executionTime"] = self.executionTime
        self.info["lastUsed"] = self.endTime
        if tb:
            self.info["traceback"] = tb
