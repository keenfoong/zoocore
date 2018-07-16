"""This module house's the base class of a plugin manager"""

import inspect
import os

from zoo.libs.plugin import plugin
from zoo.libs.utils import modules
from zoo.libs.utils import zlogging

logger = zlogging.zooLogger


class PluginManager(object):
    """This class manages a group of plugin instance's.
    use registerPlugin(instance) to registry a instance, automatically discover plugin classes use registerByModule or
    registerByPackage(pkg.path).

    To register a list of paths use instance.registerTools()
    To find out what current plugins are loaded in memory use the instance.loadedPlugins variable to return a dictionary.
    To return all plugins currently registry use the instance.plugins variable.
    """

    def __init__(self, interface=plugin.Plugin, variableName=None):
        self.plugins = {}
        # register the plugin names by the variable, if its missing fallback to the class name
        self.variableName = variableName or ""
        self.interface = interface
        self.loadedPlugins = {}  # {className: instance}
        self.basePaths = []

    def registerPaths(self, paths):
        """This function is helper function to register a list of paths.

        :param paths: A list of module or package paths, see registerByModule() and registerByPackage() for the path format.
        :type paths: list(str)
        """
        self.basePaths.extend(paths)
        for p in paths:
            if not p or p.endswith(".pyc"):
                continue
            importedModule = None
            if os.path.exists(p) and os.path.isdir(p):
                self.registerByPackage(p)
                continue
            elif p:
                importedModule = modules.importModule(modules.asDottedPath(os.path.normpath(p)))
            if importedModule:
                self.registerByModule(importedModule)
                continue

    def registerByModule(self, module):
        """ This function registry a module by search all class members of the module and registers any class that is an
        instance of the plugin class 'zoo.libs.plugin.plugin.Plugin'

        :param module: the module path to registry, the path is a '.' separated path eg. zoo.libs.apps.tooldefintions
        :type module: str
        """
        if inspect.ismodule(module):
            for member in modules.iterMembers(module, predicate=inspect.isclass):
                self.registerPlugin(member[1])

    def registerByPackage(self, pkg):
        """This function is similar to registerByModule() but works on packages, this is an expensive operation as it
        requires a recursive search by importing all sub modules and and searching them.

        :param pkg: The package path to register eg. zoo.libs.apps
        :type pkg: str
        """
        for subModule in modules.iterModules(pkg):
            filename = os.path.splitext(os.path.basename(subModule))[0]
            if filename.startswith("__") or subModule.endswith(".pyc"):
                continue
            subModuleObj = modules.importModule(modules.asDottedPath(os.path.normpath(subModule)))
            for member in modules.iterMembers(subModuleObj, predicate=inspect.isclass):
                self.registerPlugin(member[1])

    def registerPlugin(self, classObj):
        """Registers a plugin instance to the manager

        :param classObj: the plugin instance to registry
        :type classObj: Plugin
        """
        if classObj not in self.plugins.values() and issubclass(classObj, self.interface):
            name = getattr(classObj, self.variableName) if hasattr(classObj, self.variableName) else classObj.__name__
            logger.debug("registering plugin -> {}".format(name))
            self.plugins[name] = classObj

    def loadPlugin(self, pluginName, **kwargs):
        """Loads a given plugin by name. eg plugin(manager=self)

        :param name: the plugin to load by name
        :type name: str
        """
        tool = self.plugins.get(pluginName)
        if tool:
            logger.debug("Loading Plugin -> {}".format(pluginName))
            # pass the manager into the plugin, this is so we have access to any global info
            spec= inspect.getargspec(tool.__init__)
            keywords = spec.keywords
            args = spec.args

            if (args and "manager" in args) or (keywords and "manager" in keywords):
                kwargs["manager"] = self
            self.loadedPlugins[pluginName] = tool(**kwargs)
            self.loadedPlugins[pluginName].isLoaded = True
            return self.loadedPlugins[pluginName]

    def loadAllPlugins(self):
        """Loops over all registered plugins and calls them eg. plugin(manager=self)
        """
        for plugin in self.plugins:
            self.loadPlugin(plugin)

    def getPlugin(self, name):
        """Returns the plugin instance by name

        :param name: the name of the plugin
        :type name: str
        :return: Returns the plugin isinstance or None
        :rtype: Plugin instance or None
        """
        if name in self.loadedPlugins:
            return self.loadedPlugins.get(name)
        return self.plugins.get(name)

    def unload(self, name):
        """Unload's a plugin by name from the manager

        :param name: The name of the registered plugin class.
        :type name: str
        :return: Return True if the plugin was successfully unloaded.
        :rtype: bool
        """
        plugin = self.loadedPlugins.get(name)
        if plugin and plugin.isLoaded:
            self.loadedPlugins.pop(name)
            return True
        return False
