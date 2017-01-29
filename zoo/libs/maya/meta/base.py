"""
@todo may need to create a scene cache with a attach node callback to remove node form the cache
"""
import inspect
import os
from functools import wraps

import re
from maya.api import OpenMaya as om2

from zoo.libs.maya.api import attrtypes
from zoo.libs.utils import modules
from zoo.libs.utils import zlogging
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs

logger = zlogging.zooLogger


def lockMetaManager(func):
    """Decorator function to lock and unlock the meta, designed purely for the metaclass
    """

    @wraps(func)
    def locker(*args, **kwargs):
        node = args[0]
        if node.mfn().isLocked:
            nodes.lockNode(node.mobject(), False)
        try:
            return func(*args, **kwargs)
        finally:
            if node.exists():
                nodes.lockNode(node.mobject(), True)

    return locker


def findSceneRoots():
    """Finds all meta nodes in the scene that are root meta nodes
    :return:
    :rtype:
    """
    roots = []
    for meta in iterSceneMetaNodes():
        dep = om2.MFnDependencyNode(meta)
        try:
            root = dep.findPlug("root", False).asBool()
            if root:
                roots.append(root)
        except RuntimeError:
            continue
    return roots


def filterSceneByAttributeValues(attributeNames, filter):
    """ From the all scene zoo meta nodes find all attributeNames on the node if the value of the attribute is a string
    the filter acts as a regex otherwise it'll will do a value == filter op.
    :param attributeNames: a list of attribute name to find on each node
    :type attributeNames: seq(str)
    :param filter: filters the found attributes by value
    :type filter: any maya datatype
    :return:A seq of plugs
    :rtype: seq(MPlug)
    """
    for meta in iterSceneMetaNodes():
        for attr in attributeNames:
            dep = om2.MFnDependencyNode(meta)
            try:
                plug = dep.findPlug(attr, False)
            except RuntimeError:
                continue
            value = plugs.getPlugValue(plug)
            # temp
            if isinstance(value, basestring):
                grp = re.search(filter, value)
                if grp:
                    yield plug
            else:
                if value == filter:
                    yield plug


def iterSceneMetaNodes():
    t = om2.MItDependencyNodes()
    while not t.isDone():
        node = t.thisNode()
        dep = om2.MFnDependencyNode(node)
        if dep.hasAttribute("ZOO_MClass"):
            yield node
        t.next()


class MetaRegistry(object):
    """Singleton class to handle global registration to metaclasses"""
    types = {}
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        """Overridden to make the registry a singleton"""
        if cls._instance is None:
            cls._instance = super(MetaRegistry, cls).__new__(*args, **kwargs)
        return cls._instance

    def __init__(self):
        # register the default
        self.registerMetaClasses(["zoo.libs.maya.meta.metadata"])

    @classmethod
    def getType(cls, typeName):
        if typeName in cls.types:
            return cls.types[typeName]

    @classmethod
    def registerMetaClasses(cls, paths):
        """This function is helper function to register a list of paths.

        :param paths: A list of module or package paths, see registerByModule() and registerByPackage() for the path format.
        :type paths: list(str)
        """
        for p in paths:
            if len(p.split(".")) > 1:
                importedModule = modules.importModule(p)
                p = os.path.realpath(importedModule.__file__)
                if os.path.basename(p).startswith("__"):
                    p = os.path.dirname(p)
                elif p.endswith(".pyc"):
                    p = p[:-1]
            if os.path.isdir(p):
                cls.registerByPackage(p)
                continue
            if os.path.isfile(p):
                importedModule = modules.importModule(p)
                if importedModule:
                    cls.registerByModule(importedModule)
                    continue

    @classmethod
    def registerByModule(cls, module):
        """ This function registry a module by search all class members of the module and registers any class that is an
        instance of the plugin class

        :param module: the module path to registry
        :type module: str
        """
        if isinstance(module, basestring):
            module = modules.importModule(module)
        if inspect.ismodule(module):
            for member in modules.iterMembers(module, predicate=inspect.isclass):
                cls.registerMetaClass(member[1])

    @classmethod
    def registerByPackage(cls, pkg):
        """This function is similar to registerByModule() but works on packages, this is an expensive operation as it
        requires a recursive search by importing all sub modules and and searching them.

        :param pkg: The package path to register eg. zoo.libs.apps
        :type pkg: str
        """
        visited = set()
        for subModule in modules.iterModules(pkg):
            filename = os.path.splitext(os.path.basename(subModule))[0]
            if filename.startswith("__") or filename in visited:
                continue
            visited.add(filename)
            subModuleObj = modules.importModule(subModule)
            for member in modules.iterMembers(subModuleObj, predicate=inspect.isclass):
                cls.registerMetaClass(member[1])

    @classmethod
    def registryByEnv(cls, env):
        environmentPaths = os.environ.get(env)
        if environmentPaths is None:
            raise ValueError("No environment variable with the name -> {} exists".format(env))
        environmentPaths = environmentPaths.split(os.pathsep)
        return cls.registerMetaClasses(environmentPaths)

    @classmethod
    def registerMetaClass(cls, classObj):
        """Registers a plugin instance to the manager
        :param classObj: the metaClass to registry
        :type classObj: Plugin
        """
        if issubclass(classObj, MetaBase) and classObj.__name__ not in cls.types:
            logger.debug("registering metaClass -> {}".format(classObj.__name__))
            cls.types[classObj.__name__] = classObj


class MetaBase(object):
    @staticmethod
    def classNameFromPlug(node):
        dep = om2.MFnDependencyNode(node)
        try:
            return dep.findPlug("mClass", False).asString()
        except RuntimeError:
            return ""

    def __new__(cls, *args, **kwargs):
        """Custom constructor to pull the cls type from the node if it exists and recreates the class instance
        from the registry. If that class doesnt exist then the normal __new__ behaviour will be used
        """
        node = kwargs.get("node")
        if args:
            node = args[0]
        # if the user doesn't pass a node it means they want to create it
        if not node:
            return object.__new__(cls, *args, **kwargs)
        classType = cls.classNameFromPlug(node)
        if classType == cls.__name__:
            return object.__new__(cls, *args, **kwargs)
        registeredType = MetaRegistry().getType(classType)
        if not registeredType:
            # logger.warning("Class type -> {}, doesn't exist within the registry".format(registeredType))
            return object.__new__(cls, *args, **kwargs)
        return object.__new__(registeredType, *args, **kwargs)

    def __init__(self, node=None, name="", initDefaults=True):
        if node is None:
            node = nodes.createDGNode(name or self.__class__.__name__, "network")

        self._handle = om2.MObjectHandle(node)

        if node.hasFn(om2.MFn.kDagNode):
            self._mfn = om2.MFnDagNode(node)
        else:
            self._mfn = om2.MFnDependencyNode(node)

        self.lock(True)
        if initDefaults:
            self._initMeta()

    def _initMeta(self):
        """Initializes the standard attributes for the meta nodes
        """
        if not self._mfn.hasAttribute("mClass"):
            self.addAttribute("mClass", self.__class__.__name__, attrtypes.kMFnDataString)
        if not self.hasAttribute("root"):
            self.addAttribute("root", False, attrtypes.kMFnNumericBoolean)

    def __getattr__(self, name):
        if not name.startswith("_"):
            plug = self.getAttribute(name)
            if plug is not None:
                return plug
            # search for the given method name
            elif hasattr(self._mfn, name):
                return getattr(self._mfn, name)

        return super(MetaBase, self).__getattribute__(name)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            super(MetaBase, self).__setattr__(key, value)
            return

        if self._mfn.hasAttribute(key):
            plug = self._mfn.findPlug(key, False)
            if not plug.isNull:
                if isinstance(value, om2.MPlug):
                    plugs.connectPlugs(plug, value)
                elif isinstance(value, MetaBase):
                    self.addChild(value)
                elif isinstance(value, om2.MObject) and not value.hasFn(om2.MFn.kAttribute):
                    self.connectTo(key, value)
                else:
                    self.setAttribute(plug, value)

    def __eq__(self, other):
        """Checks whether the mobjects are the same
        :type other: base.MetaBase instance
        :rtype: bool
        """
        if other is None:
            return False
        return other.mobject() == self.mobject()

    def __repr__(self):
        return "{}:{}".format(self.__class__.__name__, self.__dict__)

    def mobject(self):
        """ Returns the mobject attached to this meta node
        :return: the meta nodes mObject
        :rtype: mobject
        """
        return self._handle.object()

    def handle(self):
        """
        :return: Returns the mobjecthandle
        :rtype: MObjectHandle
        """
        return self._handle

    def mfn(self):
        """
        :return: The MFn function set for this node
        :rtype: MFnDagNode or MFnDependencyNode
        """
        return self._mfn

    def fullPathName(self):
        """Returns the fullPath name for the mfn set if the mfn
        :rtype: str
        """
        if self._handle.object().hasFn(om2.MFn.kDagNode):
            return self._mfn.fullPathName()
        return self._mfn.name()

    def exists(self):
        """Checks the existence of the node
        :return: True if still alive else False
        :rtype: bool
        """
        return self._handle.isValid() and self._handle.isAlive()

    @lockMetaManager
    def delete(self):
        """Deletes the metaNode from the scene
        """
        nodes.delete(self._handle.object())

    @lockMetaManager
    def rename(self, name):
        """Renames the node
        :param name: the new name for the name
        :type name: str
        """
        nodes.rename(self._handle.object(), name)

    def lock(self, state):
        """Locks or unlocks the metanode
        :param state: True to lock the node else False
        :type state: bool
        """
        if self._mfn.isLocked == state:
            return
        nodes.lockNode(self._handle.object(), state)

    def getAttribute(self, name, networked=False):
        """Finds and returns the MPlug associated with the attribute on meta node if it exists else None
        :param name: the attribute name to find
        :type name: str
        :param networked: whether to return the network plug, see autodesk api docs
        :type networked: bool
        :rtype: MPlug or None
        """
        if self._mfn.hasAttribute(name):
            return self._mfn.findPlug(name, networked)

    @lockMetaManager
    def addAttribute(self, name, value, Type):
        if self._mfn.hasAttribute(name):
            return
        attr = nodes.addAttribute(self._handle.object(), name, name, Type)
        newPlug = None
        if attr is not None:
            newPlug = om2.MPlug(self._handle.object(), attr.object())
        if value is not None and newPlug is not None:
            # if mobject expect it to be a node
            if isinstance(value, om2.MObject):
                self.connectTo(name, value)
            else:
                plugs.setAttr(newPlug, value)
        newPlug.isLocked = True
        return attr

    def setAttribute(self, attr, value):
        if isinstance(attr, om2.MPlug):
            with plugs.setLockedContext(attr):
                plugs.setAttr(attr, value)
            return
        if self.hasAttribute(attr):
            plug = self._mfn.findPlug(attr, False)
            with plugs.setLockedContext(plug):
                plugs.setAttr(plug, value)

    @lockMetaManager
    def removeAttribute(self, name):
        if self._mfn.hasAttribute(name):
            plug = self._mfn.findPlug(name, False)
            if plug.isLocked:
                plug.isLocked = False
            mod = om2.MDGModifier()
            mod.removeAttribute(self._handle.object(), plug.asMObject())
            mod.doIt()
            return True
        return False

    def hasAttribute(self, name):
        return self._mfn.hasAttribute(name)

    @lockMetaManager
    def renameAttribute(self, name, newName):
        try:
            plug = self._mfn.findPlug(name, False)
        except RuntimeError:
            raise AttributeError("No attribute named {} on metaNode->{}".format(name, self.fullPathName()))
        with plugs.setLockedContext(plug):
            mod = om2.MDGModifier()
            mod.renameAttribute(self.mobject(), plug.attribute(), newName, newName)
            mod.doIt()
        return True

    def iterAttributes(self):
        node = self._mfn
        for i in range(node.attributeCount()):
            yield node.findPlug((node.attribute(i)), False)

    def findPlugsByFilteredName(self, filter=""):
        """Finds all plugs with the given filter with in name
        :param filter: the string the search the names by
        :type filter: str
        :return: A seq of MPlugs
        :rtype: seq(MPlug)
        """
        plugs = []
        for i in self.iterAttributes():
            grp = re.search(filter, i.name())
            if grp:
                plugs.append(i)
        return plugs

    def findPlugsByType(self, filterType=om2.MFnMessageAttribute):
        plugs = []
        for plug in self.iterAttributes():
            objAttr = plug.attribute()
            if objAttr.hasFn(filterType):
                plugs.append(plug)
        return plugs

    def findConnectedNodes(self, attributeName="", filter=""):
        if attributeName:
            if not self._mfn.hasAttribute(attributeName):
                raise AttributeError()
            filteredNodes = plugs.filterConnectedNodes(self._mfn.findPlug(attributeName, False), filter, True, True)
            return filteredNodes
        filteredNodes = []
        for i in self.iterAttributes():
            filtered = plugs.filterConnectedNodes(i, filter, True, True)
            filteredNodes.extend(filtered)
        return filteredNodes

    def serialize(self):
        data = {}
        for plug in self.iterAttributes():
            attrData = {"name": plug.name(),
                        "type": plug.attribute().apiTypeStr,
                        "value": plugs.getPlugValue(plug)}
            connections = []
            if plug.isSource:
                for connection in plug.connectedTo(False, True):
                    connections.append((nodes.nameFromMObject(connection.node()), connection.name()))
            attrData["connections"] = connections
            data.update(attrData)
        return data

    def connectTo(self, attributeName, node, nodeAttributeName=None):
        nodeAttributeName = nodeAttributeName or "metaNode"
        dep = om2.MFnDependencyNode(node)
        if not dep.hasAttribute(nodeAttributeName):
            destinationPlug = dep.findPlug(nodes.addAttribute(node, nodeAttributeName, nodeAttributeName,
                                                              attrtypes.kMFnMessageAttribute).object(), False)
        else:
            destinationPlug = dep.findPlug(nodeAttributeName, False)
            if destinationPlug.isDestination:
                mod = om2.MDGModifier()
                mod.disconnect(destinationPlug.connectedTo(True, False)[0], destinationPlug)
                mod.doIt()

        if self._mfn.hasAttribute(attributeName):
            # we should have been disconnected from the destination control above
            sourcePlug = self._mfn.findPlug(attributeName, False)
        else:
            newAttr = self.addAttribute(attributeName, None, attrtypes.kMFnMessageAttribute)
            if newAttr is not None:
                sourcePlug = self._mfn.findPlug(newAttr.object(), False)
            else:
                sourcePlug = self._mfn.findPlug(attributeName, False)
        with plugs.setLockedContext(sourcePlug):
            plugs.connectPlugs(sourcePlug, destinationPlug)
        return destinationPlug
