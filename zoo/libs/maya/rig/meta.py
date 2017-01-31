from maya.api import OpenMaya as om2

from zoo.libs.maya.meta import metadata
from zoo.libs.maya.meta import base
from zoo.libs.maya.api import attrtypes


class MetaRig(metadata.MetaNode):
    _ctrlPrefix = "CTRL"
    _jntPrefix = "JNT"
    _skinJntPrefix = "SKIN"
    _geoPrefix = "GEO"

    def _initMeta(self):
        super(MetaRig, self)._initMeta()
        self.addAttribute("version", "1.0.0", attrtypes.kMFnDataString)

    def addControl(self, node, name):
        attrname = "_".join([self._ctrlPrefix, name])
        return self.connectTo(attrname, node)

    def addJoint(self, node, name):
        attrname = "_".join([self._jntPrefix, name])
        return self.connectTo(attrname, node)

    def addSkinJoint(self, node, name):
        attrname = "_".join([self._skinJntPrefix, name])
        return self.connectTo(attrname, node)

    def addGeo(self, node, name):
        attrname = "_".join([self._geoPrefix, name])
        return self.connectTo(attrname, node)

    def controls(self, recursive=True):
        ctrls = self.findPlugsByFilteredName(self._ctrlPrefix)
        if recursive:
            for m in self.iterMetaChildren():
                ctrls.extend(m.findPlugsByFilteredName(self._ctrlPrefix))

        return ctrls

    def joints(self, recursive=True):
        jnts = self.findPlugsByFilteredName(self._jntPrefix)
        if recursive:
            for m in self.iterMetaChildren():
                jnts.extend(m.findPlugsByFilteredName(self._jntPrefix))
        return jnts

    def skinJoints(self, recursive):
        skJnts = self.findPlugsByFilteredName(self._skinJntPrefix)
        if recursive:
            for m in self.iterMetaChildren():
                skJnts.extend(m.findPlugsByFilteredName(self._skinJntPrefix))
        return skJnts

    def geo(self, recursive=True):
        geos = self.findPlugsByFilteredName(self._geoPrefix)
        if recursive:
            for m in self.iterMetaChildren():
                geos.extend(m.findPlugsByFilteredName(self._geoPrefix))
        return geos

    def filterSubSystemByName(self, name):
        for subsys in iter(self.subSystems()):
            if subsys.name.asString() == name:
                return subsys
        return None

    def filterSupportSystemByName(self, name):
        for subsys in iter(self.supportSystems()):
            if subsys.name.asString() == name:
                return subsys
        return None

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

    def supportSystems(self):
        if isinstance(self, MetaSupportSystem):
            return
        if self._mfn.hasAttribute("supportSystem"):
            plug = self._mfn.findPlug("supportSystem", False)
            if plug.isSource:
                connections = plug.destinations()
                return [MetaSupportSystem(i.node()) for i in connections]
        return []

    def subSystems(self):
        if isinstance(self, MetaSubSystem):
            return
        if self._mfn.hasAttribute("subSystem"):
            plug = self._mfn.findPlug("subSystem", False)
            if plug.isSource:
                connections = plug.destinations()
                return [MetaSubSystem(i.node()) for i in connections]
        return []

    def addSupportSystem(self, node=None, name=None):
        if node is None:
            name = "subsystem_#" if not name else "_".join([name, "meta"])
            node = MetaSupportSystem(name=name).object()
        elif isinstance(node, om2.MObject):
            node = MetaSupportSystem(node)

        self.connectTo("supportSystem", node.mobject(), "metaParent")

        return node

    def addSubSystem(self, node=None, name=None):
        if node is None:
            name = "sub_meta#" if not name else "_".join([name, "meta"])
            node = MetaSubSystem(name=name)
        elif isinstance(node, om2.MObject):
            node = MetaSubSystem(node)

        self.connectTo("subSystem", node.mobject(), "metaParent")

        return node


class MetaSupportSystem(MetaRig):
    def __init__(self, node=None, name="", initDefaults=True):
        super(MetaRig, self).__init__(node, name, initDefaults)

    def _initMeta(self):
        super(MetaSupportSystem, self)._initMeta()
        self.addAttribute(name="name", value="", Type=attrtypes.kMFnDataString)


class MetaSubSystem(MetaRig):
    def __init__(self, node=None, name="", initDefaults=True):
        super(MetaRig, self).__init__(node, name, initDefaults)

    def _initMeta(self):
        super(MetaSubSystem, self)._initMeta()
        self.addAttribute(name="name", value="", Type=attrtypes.kMFnDataString)


# temp registration
base.MetaRegistry().registerMetaClass(MetaRig)
base.MetaRegistry().registerMetaClass(MetaSupportSystem)
base.MetaRegistry().registerMetaClass(MetaSubSystem)
