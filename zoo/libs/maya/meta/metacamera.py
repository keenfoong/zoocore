from maya.api import OpenMaya as om2

from zoo.libs.maya.meta import base
from zoo.libs.maya.api import attrtypes, nodes


class MetaCamera(base.MetaBase):
    """Wrapper for camera shape nodes to add generic meta data of the start/end frame
    camera_version number and shot_name
    """
    def __init__(self, node=None, name=None, initDefaults=True):
        super(MetaCamera, self).__init__(node, name, initDefaults)
        if self._handle.object().apiType() == om2.MFn.kCamera:
            self._mfn = om2.MFnCamera(self._handle.object())

    def _initMeta(self):
        super(MetaCamera, self)._initMeta()
        self.addAttribute("isCamera", True, attrtypes.kMFnNumericBoolean)
        self.addAttribute("startFrame", 0, attrtypes.kMFnNumericInt)
        self.addAttribute("endFrame", 0, attrtypes.kMFnNumericInt)
        self.addAttribute("shotName", "", attrtypes.kMFnDataString)
        self.addAttribute("cameraVersion", 1, attrtypes.kMFnNumericInt)

    @base.lockMetaManager
    def delete(self):
        fn = self._mfn
        if fn.object().apiType() == om2.MFn.kCamera:
            node = nodes.getParent(fn.object())
        else:
            node = fn.object()

        nodes.delete(node)

    @base.lockMetaManager
    def rename(self, name):
        """Renames the camera node if the node is kCamera type then the parent transform will
        be renamed instead of the shape.

        :param name: the new name for the node.
        :type name: str
        """
        fn = self.mfn()

        if fn.object().apiType() == om2.MFn.kCamera:
            node = nodes.getParent(fn.object())
        else:
            node = fn.object()
        nodes.rename(node, name)
