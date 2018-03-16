import inspect
import os

from zoo.libs.utils import zlogging
from zoo.libs.command import command
from zoo.libs.utils import modules

logger = zlogging.zooLogger


def registerCommands(paths):
    """This function is helper function to register a list of paths.

    :param paths: A list of module or package paths, see registerByModule() and registerByPackage() for the path format.
    :type paths: list(str)
    """
    commands = []
    for p in paths:
        if p.endswith(".pyc"):
            continue
        elif os.path.isdir(p):
            commands.extend(registerByPackage(p))
            continue
        elif os.path.isfile(p):
            importedModule = modules.importModule(p)
            if importedModule:
                commands.extend(registerByModule(importedModule))
                continue
        # case where the user pass the python path like so , zoo.libs.somelib
        elif len(p.split(".")) > 1:
            importedModule = modules.importModule(p)
            p = os.path.realpath(importedModule.__file__)
            if os.path.basename(p).startswith("__"):
                p = os.path.dirname(p)
            elif p.endswith(".pyc"):
                p = p[:-1]
    return commands


def registerByModule(module):
    """ This function registry a module by search all class members of the module and registers any class that is an
    instance of the plugin class

    :param module: the module path to registry
    :type module: str
    """
    if isinstance(module, basestring):
        module = modules.importModule(module)
    commands = []
    if inspect.ismodule(module):
        for member in modules.iterMembers(module, predicate=inspect.isclass):
            commands.append(registerCommand(member[1]))

    return commands


def registerByPackage( pkg):
    """This function is similar to registerByModule() but works on packages, this is an expensive operation as it
    requires a recursive search by importing all sub modules and and searching them.

    :param pkg: The package path to register eg. zoo.libs.apps
    :type pkg: str
    """
    visited = set()
    commands = []
    for subModule in modules.iterModules(pkg):
        filename = os.path.splitext(os.path.basename(subModule))[0]
        if filename.startswith("__") or subModule.endswith(".pyc") or filename in visited:
            continue
        visited.add(filename)
        subModuleObj = modules.importModule(subModule)
        for member in modules.iterMembers(subModuleObj, predicate=inspect.isclass):
            newCom = registerCommand(member[1])
            if newCom:
                commands.append(newCom)
    return commands


def registryByEnv( env):
    environmentPaths = os.environ.get(env)
    if environmentPaths is None:
        raise ValueError("No environment variable with the name -> {} exists".format(env))
    environmentPaths = environmentPaths.split(os.pathsep)
    return registerCommands(environmentPaths)


def registerCommand( classObj):
    """Registers a plugin instance to the manager

    :param classObj: the plugin instance to registry
    :type classObj: Plugin
    """
    if issubclass(classObj, command.ZooCommand):
        logger.debug("registering plugin -> {}".format(classObj.__name__))
        return classObj
