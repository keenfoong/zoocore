from maya.api import OpenMaya as om2

from zoo.libs.maya.meta import base
from zoo.libs.maya.api import attrtypes


class MetaRig(base.MetaBase):
    icon = "user"
    _ctrlPrefix = "CTRL"
    _jntPrefix = "JNT"
    _skinJntPrefix = "SKIN"
    _geoPrefix = "GEO"
    _proxyGeoPrefix = "GEO_PROXY"
    _rootPrefix = "ROOT"

    def _initMeta(self):
        super(MetaRig, self)._initMeta()
        self.addAttribute(name="name", value="", Type=attrtypes.kMFnDataString)

    def addRootNode(self, node, name):
        attrname = "_".join([self._rootPrefix, name])
        return self.connectTo(attrname, node)

    def addControl(self, node, name):
        attrname = "_".join([self._ctrlPrefix, name])
        return self.connectTo(attrname, node)

    def addJoint(self, node, name):
        attrname = "_".join([self._jntPrefix, name])
        return self.connectTo(attrname, node)

    def addSkinJoint(self, node, name):
        attrname = "_".join([self._skinJntPrefix, name])
        return self.connectTo(attrname, node)

    def addProxyGeo(self, node, name):
        attrname = "_".join([self._proxyGeoPrefix, name])
        return self.connectTo(attrname, node)

    def addGeo(self, node, name):
        attrname = "_".join([self._geoPrefix, name])
        return self.connectTo(attrname, node)
    def proxyGeo(self, recursive=True):
        return self.findConnectedNodesByAttributeName(self._proxyGeoPrefix, recursive=recursive)

    def addIkJoint(self, joint, name):
        self.addJoint(joint, "_".join([self._ikPrefix, name, "jnt"]))

    def addFkJoint(self, joint, name):
        self.addJoint(joint, "_".join([self._fkPrefix, name, "jnt"]))

    def addIkControl(self, ctrl, name):
        self.addControl(ctrl, "_".join([self._ikPrefix, name, "anim"]))

    def addFkControl(self, ctrl, name):
        self.addControl(ctrl, "_".join([self._fkPrefix, name, "anim"]))

    def control(self, name, recursive):
        results = self.findConnectedNodesByAttributeName("_".join([self._ctrlPrefix, name]), recursive=recursive)
        if results:
            return results[0]
        return None

    def controls(self, recursive=True):
        return self.findConnectedNodesByAttributeName(self._ctrlPrefix, recursive=recursive)

    def joints(self, recursive=True):
        return self.findConnectedNodesByAttributeName(self._jntPrefix, recursive=recursive)

    def skinJoints(self, recursive):
        return self.findConnectedNodesByAttributeName(self._jntPrefix, recursive=recursive)

    def geo(self, recursive=True):
        return self.findConnectedNodesByAttributeName(self._geoPrefix, recursive=recursive)

    def filterSubSystemByName(self, name):
        for subsys in iter(self.subSystems()):
            if subsys.getAttribute("name").asString() == name:
                return subsys
        return None

    def filterSupportSystemByName(self, name):
        for subsys in iter(self.supportSystems()):
            if subsys.name.asString() == name:
                return subsys
        return None

    def isSubSystem(self):
        return isinstance(self, MetaSubSystem)

    def isSupportSystem(self):
        return isinstance(self, MetaSupportSystem)

    def hasSupportSystemByName(self, name):
        for subsys in iter(self.supportSystems()):
            if subsys.name.asString() == name:
                return True
        return False

    def hasSubSystemName(self, name):
        for subsys in iter(self.subSystems()):
            if subsys.name.asString() == name:
                return True
        return False

    def addSupportSystem(self, node=None, name=None):
        if node is None:
            name = "subsystem_#" if not name else "_".join([name, "meta"])
            node = MetaSupportSystem(name=name).object()
        elif isinstance(node, om2.MObject):
            node = MetaSupportSystem(node)

        self.connectTo("supportSystem", node.mobject(), base.MPARENT_ATTR_NAME)

        return node

    def addSubSystem(self, node=None, name=None):
        if node is None:
            node = MetaSubSystem(name=name)
        elif isinstance(node, om2.MObject):
            node = MetaSubSystem(node)

        self.connectTo("subSystem", node.mobject(), base.MPARENT_ATTR_NAME)

        return node

    def supportSystems(self):
        if isinstance(self, MetaSupportSystem):
            return
        if self._mfn.hasAttribute("supportSystem"):
            plug = self._mfn.findPlug("supportSystem", False)
            if plug.isSource:
                connections = plug.destinations()
                return [MetaSupportSystem(i.node()) for i in connections]
        return []

    def iterSupportSystems(self):
        if isinstance(self, MetaSubSystem):
            return
        if self._mfn.hasAttribute("supportSystem"):
            plug = self._mfn.findPlug("supportSystem", False)
            if plug.isSource:
                connections = plug.destinations()
                for i in connections:
                    yield MetaSupportSystem(i.node())

    def iterSubSystems(self):
        if isinstance(self, MetaSubSystem):
            return
        if self._mfn.hasAttribute("subSystem"):
            plug = self._mfn.findPlug("subSystem", False)
            if plug.isSource:
                connections = plug.destinations()
                for i in connections:
                    yield MetaSubSystem(i.node())

    def subSystems(self):
        if isinstance(self, MetaSubSystem):
            return
        if self._mfn.hasAttribute("subSystem"):
            plug = self._mfn.findPlug("subSystem", False)
            if plug.isSource:
                connections = plug.destinations()
                return [MetaSubSystem(node=i.node()) for i in connections]
        return []


class MetaSupportSystem(MetaRig):
    def __init__(self, node=None, name=None, initDefaults=True):
        super(MetaRig, self).__init__(node, name, initDefaults)


class MetaSubSystem(MetaRig):
    def __init__(self, node=None, name="", initDefaults=True):
        super(MetaRig, self).__init__(node, name, initDefaults)
