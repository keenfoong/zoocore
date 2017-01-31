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

    def controls(self):
        return self.findPlugsByFilteredName(self._ctrlPrefix)

    def joints(self):
        return self.findPlugsByFilteredName(self._jntPrefix)

    def skinJoints(self):
        return self.findPlugsByFilteredName(self._skinJntPrefix)

    def geo(self):
        return self.findPlugsByFilteredName(self._geoPrefix)

    def supportSystems(self):
        if self.mClass.asString() == "MetaSupport":
            return None
        if self._mfn.hasAttribute("supportSystem"):
            plug = self._mfn.findPlug("supportSystem", False)
            if plug.isSource:
                connections = plug.destinations()
                return [MetaSupport(i.node()) for i in connections]

    def subSystems(self):
        if self.mClass.asString() == "MetaSubSystem":
            return None
        if self._mfn.hasAttribute("subSystem"):
            plug = self._mfn.findPlug("subSystem", False)
            if plug.isSource:
                connections = plug.destinations()
                return [MetaSubSystem(i.node()) for i in connections]

    def addSupportSystem(self, node=None, name=None):
        if node is not None:
            if isinstance(node, base.MetaBase):
                node = node.mobject()
        else:
            node = MetaSupport(name=name or "support_meta_#").object()
        self.connectTo("supportSystem", node, "metaParent")

        return node

    def addSubSystem(self, node=None, name=None):
        if node is not None:
            if isinstance(node, base.MetaBase):
                node = node.mobject()
        else:
            node = MetaSupport(name=name or "sub_meta_##").object()
        self.connectTo("subSystem", node, "metaParent")

        return node


class MetaSupport(MetaRig):
    def __init__(self, node=None, name="", initDefaults=True):
        super(MetaRig, self).__init__(node, name, initDefaults)


class MetaSubSystem(MetaRig):
    def __init__(self, node=None, name="", initDefaults=True):
        super(MetaRig, self).__init__(node, name, initDefaults)


# temp registration
base.MetaRegistry().registerMetaClass(MetaRig)
base.MetaRegistry().registerMetaClass(MetaSupport)
base.MetaRegistry().registerMetaClass(MetaSubSystem)
