import uuid
import re

from maya.api import OpenMaya as om2
from zoo.libs.utils import zlogging
from zoo.libs.maya.api import plugs
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import attrtypes
from zoo.libs.maya.meta import base as metabase

logger = zlogging.zooLogger


class MetaNode(metabase.MetaBase):
    def metaClassPlug(self):
        try:
            return self._mfn.findPlug("mClass", False)
        except RuntimeError:
            return None

    def __init__(self, node=None, name="", initDefaults=True):
        super(MetaNode, self).__init__(node, name, initDefaults)

    def _initMeta(self):
        super(MetaNode, self)._initMeta()
        if not self.hasAttribute("uuid"):
            self.addAttribute("uuid", str(uuid.uuid4()), attrtypes.kMFnDataString)
        if not self.hasAttribute("metaParent"):
            self.addAttribute("metaParent", None, attrtypes.kMFnMessageAttribute)
        if not self.hasAttribute("metaChildren"):
            self.addAttribute("metaChildren", None, attrtypes.kMFnMessageAttribute)

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
            return MetaNode(parentPlug.connectedTo(True, False)[0].node())

    def metaChildren(self):
        return [i for i in self.iterMetaChildren()]

    def iterMetaChildren(self, depthLimit=256):
        childPlug = self._mfn.findPlug("metaChildren", False)
        for child in plugs.iterDependencyGraph(childPlug, depthLimit=depthLimit):
            yield MetaNode(child.node())

    def addChild(self, child):
        child.removeParent()
        child.addParent(self)

    def addParent(self, parent):
        metaParent = self.metaParent()
        if metaParent is not None or metaParent == parent:
            raise ValueError("MetaNode already has a parent, call removeParent first")
        parentPlug = self._mfn.findPlug("metaParent", False)
        with plugs.setLockedContext(parentPlug):
            plugs.connectPlugs(parent.findPlug("metaChildren", False), parentPlug)

    def findChildrenByFilter(self, filter):
        children = []
        for child in self.iterMetaChildren():
            grp = re.search(filter, nodes.nameFromMObject(child))
            if grp:
                children.append(child)
        return children

    def findChildByType(self, Type):
        children = []
        for child in self.iterMetaChildren(depthLimit=1):
            if child.apiType() == Type:
                children.append(child)
        return children

    def removeParent(self):
        parent = self.metaParent()
        if parent is None:
            return
        mod = om2.MDGModifier()
        source= parent.findPlug("metaChildren", False)
        destination = self.findPlug("metaParent", False)
        with plugs.setLockedContext(source):
            destination.isLocked = False
            mod.disconnect(source, destination)
            mod.doIt()

    def removeChild(self, node):
        if isinstance(node, metabase.MetaBase):
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