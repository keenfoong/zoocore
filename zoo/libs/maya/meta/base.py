"""
@todo may need to create a scene cache with a attach node callback to remove node form the cache
"""
import inspect
import os
from functools import wraps
import uuid
import re

from maya.api import OpenMaya as om2
from zoo.libs.utils import modules
from zoo.libs.utils import zlogging
from zoo.libs.utils import classtypes
from zoo.libs.maya.api import plugs
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import attrtypes

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
    """Finds all meta nodes in the scene that are root meta node
    :return:
    :rtype: list()
    """
    roots = []
    for meta in iterSceneMetaNodes():
        dep = om2.MFnDependencyNode(meta)
        try:
            isRoot = dep.findPlug("root", False).asBool()
            if isRoot:
                roots.append(MetaBase(node=meta))
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
        dep = om2.MFnDependencyNode(meta)
        for attr in attributeNames:
            try:
                plug = dep.findPlug(attr, False)
            except RuntimeError:
                continue
            value = plugs.getPlugValue(plug)
            if isinstance(value, basestring):
                grp = re.search(filter, value)
                if grp:
                    yield plug
            elif value == filter:
                yield plug


def iterSceneMetaNodes():
    """Iterates all metanodes in the maya scene
    :rtype: Generator(MObject)
    """
    t = om2.MItDependencyNodes()
    while not t.isDone():
        node = t.thisNode()
        dep = om2.MFnDependencyNode(node)
        if dep.hasAttribute("mClass"):
            yield node
        t.next()


def isMetaNode(node):
    """Determines if the node is a meta node by seeing if the attribute mnode exists and mclass value(classname) is
    within the current meta registry
    :param node:
    :type node: MObject
    :rtype: bool
    """
    if isinstance(node, MetaBase) or issubclass(type(node), MetaBase):
        return True
    dep = om2.MFnDependencyNode(node)
    if dep.hasAttribute("mClass"):
        return MetaRegistry.isInRegistry(dep.findPlug("mClass", False).asString())
    return False


def getConnectedMetaNodes(node):
    mNodes = []
    for dest, source in nodes.iterConnections(node, True, False):
        node = source.node()
        if isMetaNode(node):
            mNodes.append(MetaBase(node))
    return mNodes


class MetaRegistry(object):
    """Singleton class to handle global registration to metaclasses"""
    __metaclass__ = classtypes.Singleton
    metaEnv = "ZOO_META_PATHS"
    types = {}

    def __init__(self):
        try:
            self.registryByEnv(MetaRegistry.metaEnv)
        except ValueError:
            pass

    @classmethod
    def isInRegistry(cls, typeName):
        "Checks to see if the type is currently available in the registry"
        return typeName in cls.types

    @classmethod
    def getType(cls, typeName):
        """Returns the class of the type
        :param typeName: the class name
        :type typeName: str
        :return: returns the class object for the given type name
        :rtype: object
        """
        return cls.types.get(typeName)

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


class MetaFactory(type):
    """MetaClass for metabase class to create the correct metaBase subclass based on class plug name if a meta
    node(MObject) exists in the arguments"""

    def __call__(cls, *args, **kwargs):
        """Custom constructor to pull the cls type from the node if it exists and recreates the class instance
        from the registry. If that class doesnt exist then the normal __new__ behaviour will be used
        """
        node = kwargs.get("node")
        if args:
            node = args[0]
        # if the user doesn't pass a node it means they want to create it
        if not node:
            return type.__call__(cls, *args, **kwargs)
        classType = MetaBase.classNameFromPlug(node)
        if classType == cls.__name__:
            return type.__call__(cls, *args, **kwargs)

        registeredType = MetaRegistry().getType(classType)
        if registeredType is None:
            return type.__call__(cls, *args, **kwargs)
        return type.__call__(registeredType, *args, **kwargs)


class MetaBase(object):
    __metaclass__ = MetaFactory

    @staticmethod
    def classNameFromPlug(node):
        """Given the MObject node or metaClass return the associated class name which should exist on the maya node
        as an attribute
        :param node: the node to find the class name for
        :type node: MObject or MetaBase instance
        :return:  the mClass name
        :rtype: str
        """
        if isinstance(node, MetaBase):
            return node.mClass.asString()
        dep = om2.MFnDependencyNode(node)
        try:
            return dep.findPlug("mClass", False).asString()
        except RuntimeError:
            return ""

    def __init__(self, node=None, name=None, initDefaults=True):
        if node is None:
            name = "_".join([name or self.__class__.__name__, "meta"])
            node = nodes.createDGNode(name, "network")

        self._handle = om2.MObjectHandle(node)

        if node.hasFn(om2.MFn.kDagNode):
            self._mfn = om2.MFnDagNode(node)
        else:
            self._mfn = om2.MFnDependencyNode(node)
        if initDefaults and not self._mfn.hasAttribute("mClass"):
            self._initMeta()
        if not self._mfn.isLocked:
            self.lock(True)

    def _initMeta(self):
        """Initializes the standard attributes for the meta nodes
        """
        self.addAttribute("mClass", self.__class__.__name__, attrtypes.kMFnDataString)
        self.addAttribute("version", "1.0.0", attrtypes.kMFnDataString)
        self.addAttribute("root", False, attrtypes.kMFnNumericBoolean)
        self.addAttribute("uuid", str(uuid.uuid4()), attrtypes.kMFnDataString)
        self.addAttribute("metaParent", None, attrtypes.kMFnMessageAttribute)
        self.addAttribute("metaChildren", None, attrtypes.kMFnMessageAttribute)

    def __getattr__(self, name):
        if name.startswith("_"):
            super(MetaBase, self).__getattribute__(name)
            return
        plug = self.getAttribute(name)
        if plug is not None:
            if plug.isSource:
                return [i.node() for i in plug.destinations()]
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
        if not self.exists():
            raise ValueError("Meta node no longer exists in the scene")
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
        metaMobj = self._handle.object()
        nodes.delete(metaMobj)

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
        try:
            attr = nodes.addAttribute(self._handle.object(), name, name, Type)
        except RuntimeError:
            return
        newPlug = None
        if attr is not None:
            newPlug = om2.MPlug(self._handle.object(), attr.object())

        if value is not None and newPlug is not None:
            # if mobject expect it to be a node
            if isinstance(value, om2.MObject):
                self.connectTo(name, value)
            else:
                plugs.setPlugValue(newPlug, value)
        newPlug.isLocked = True
        return attr

    def setAttribute(self, attr, value):
        if isinstance(attr, om2.MPlug):
            with plugs.setLockedContext(attr):
                plugs.setPlugValue(attr, value)
            return
        if self.hasAttribute(attr):
            plug = self._mfn.findPlug(attr, False)
            with plugs.setLockedContext(plug):
                plugs.setPlugValue(plug, value)

    @lockMetaManager
    def removeAttribute(self, name):
        if not self.exists():
            return False
        if self._mfn.hasAttribute(name):
            plug = self._mfn.findPlug(name, False)
            if plug.isLocked:
                plug.isLocked = False
            mod = om2.MDGModifier()
            mod.removeAttribute(self._handle.object(), plug.attribute())
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
        for i in nodes.iterAttributes(self.mobject()):
            yield i

    def findConnectedNodesByAttributeName(self, filter, recursive=False):
        plugs = self.findPlugsByFilteredName(filter)
        results = []
        for p in iter(plugs):
            if p.isSource:
                results.extend([i.node() for i in p.destinations()])
        if recursive:
            for m in iter(self.iterMetaChildren()):
                for p in iter(m.findPlugsByFilteredName(filter)):
                    if p.isSource:
                        results.extend([i.node() for i in p.destinations()])
        return results

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
            plugs.disconnectPlug(destinationPlug)

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
            if destinationPlug.isLocked:
                destinationPlug.isLocked = False
            plugs.connectPlugs(sourcePlug, destinationPlug)
            destinationPlug.isLocked = True
        return destinationPlug

    def metaRoot(self):
        parent = self.metaParent()
        while parent is not None:
            coParent = parent.metaParent()
            if coParent is not None and coParent.root.asBool():
                return coParent
            parent = coParent

    def metaParent(self):
        parentPlug = self._mfn.findPlug("metaParent", False)
        if parentPlug.isConnected:
            return MetaBase(parentPlug.connectedTo(True, False)[0].node())

    def iterParents(self, depthLimit=256):
        parentPlug = self._mfn.findPlug("metaParent", False)
        for parent in plugs.iterDependencyGraph(parentPlug, depthLimit=depthLimit, transverseType="up"):
            yield MetaBase(parent.node())

    def metaChildren(self, depthLimit=256):
        return [i for i in self.iterMetaChildren(depthLimit=depthLimit)]

    def iterMetaChildren(self, depthLimit=256):
        """This function iterate the meta children by the metaChildren Plug and return the metaBase instances
        
        :param depthLimit: The travsal depth limit
        :type depthLimit: int
        :return: A list of Metabase instances
        :rtype: list(MetaBase)
        """
        childPlug = self._mfn.findPlug("metaChildren", False)
        for child in plugs.iterDependencyGraph(childPlug, depthLimit=depthLimit):
            yield MetaBase(child.node())

    def iterMetaTree(self, depthLimit=256):
        """This function traverses the meta tree pulling out any meta node this is done by checking each node 
        has the mclass Attribute. This function can be slow depending on the size of the tree 
        
        :param depthLimit: 
        :type depthLimit: int
        :rtype: generator(MetaBase)
        """
        if depthLimit < 1:
            return
        for source, destination in nodes.iterConnections(self.mobject(), False, True):
            node = destination.node()
            if isMetaNode(node):
                m = MetaBase(node)
                yield m
                for i in m.iterMetaTree(depthLimit=depthLimit - 1):
                    yield i

    def addChild(self, child):
        child.removeParent()
        child.addParent(self)

    def addParent(self, parent):
        """Sets the parent meta node for this node, removes the previous parent if its attached
        
        :param parent: The meta node to add as the parent of this meta node 
        :type parent: MetaBase
        :todo: change the method name to setParent since we should only allow one parent
        """
        if isinstance(parent, om2.MObject):
            parent = MetaBase(parent)
        metaParent = self.metaParent()
        if metaParent is not None or metaParent == parent:
            self.removeParent()
        parentPlug = self._mfn.findPlug("metaParent", False)
        with plugs.setLockedContext(parentPlug):
            plugs.connectPlugs(parent.findPlug("metaChildren", False), parentPlug)

    def findChildrenByFilter(self, filter, plugName=None):
        children = []
        for child in self.iterMetaChildren():
            if not plugName:
                grp = re.search(filter, nodes.nameFromMObject(child))
            else:
                try:
                    plug = child._mfn.findPlug(plugName, False)
                    grp = re.search(filter, plugs.getPlugValue(plug))
                except RuntimeError:
                    continue
            if grp:
                children.append(child)
        return children

    def findChildByType(self, Type):
        children = []
        for child in self.iterMetaChildren(depthLimit=1):
            if child.apiType() == Type:
                children.append(child)
        return children

    def allChildrenNodes(self, recursive=False):
        children = []
        for source, destination in nodes.iterConnections(self.mobject(), False, True):
            node = destination.node()
            if node not in children:
                children.append(destination.node())
        if recursive:
            for child in self.iterMetaChildren():
                children.extend([i for i in child.allChildrenNodes() if i not in children])
        return children

    def removeParent(self):
        parent = self.metaParent()
        if parent is None:
            return False
        mod = om2.MDGModifier()
        source = parent.findPlug("metaChildren", False)
        destination = self.findPlug("metaParent", False)
        with plugs.setLockedContext(source):
            destination.isLocked = False
            mod.disconnect(source, destination)
            mod.doIt()
        return True

    def removeChild(self, node):
        """Removes the meta child from this node which should currently be the meta parent
        :param node:
        :type node: MObject or MetaBase instance
        :return: True if removed
        :rtype: bool
        """
        if isinstance(node, MetaBase):
            node.removeParent()
            return True
        childPlug = self._mfn.findPlug("metaChildren", False)
        mod = om2.MDGModifier()
        destination = om2.MFnDependencyNode(node).findPlug("metaParent", False)
        with plugs.setLockedContext(childPlug):
            destination.isLocked = False
        mod.disconnect(childPlug, destination)
        mod.doIt()
        return True
