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

    def addJnt(self, node, name):
        attrname = "_".join([self._jntPrefix, name])
        return self.connectTo(attrname, node)

    def addSkinJnt(self, node, name):
        attrname = "_".join([self._skinJntPrefix, name])
        return self.connectTo(attrname, node)

    def addGeo(self, node, name):
        attrname = "_".join([self._geoPrefix, name])
        return self.connectTo(attrname, node)

    def controls(self):
        return self.findPlugsByFilteredName(self._ctrlPrefix)

    def jnts(self):
        return self.findPlugsByFilteredName(self._jntPrefix)

    def skinJnts(self):
        return self.findPlugsByFilteredName(self._skinJntPrefix)

    def geo(self):
        return self.findPlugsByFilteredName(self._geoPrefix)


base.MetaRegistry().registerMetaClass(MetaRig)
