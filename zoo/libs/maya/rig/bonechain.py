from maya.api import OpenMaya as om2
from maya import cmds

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs
from zoo.libs.maya.rig import control
from zoo.libs.utils import zlogging

logger = zlogging.getLogger(__name__)


class BoneChain(object):
    def __init__(self, joints=None):
        self.joints = joints or []

    def create(self, names, positions, orientations=None, rotationOrders=None):
        if self.joints:
            raise ValueError("Already created joints!")
        for i in xrange(len(positions)):
            cmds.select(cl=True)

            if orientations:
                tempJnt = cmds.joint(n=names[i], position=positions[i], orientation=orientations[i])

            else:
                tempJnt = cmds.joint(n=names[i], position=positions[i])

            self.joints.append(om2.MObjectHandle(nodes.asMObject(tempJnt)))

        revList = list(self.joints)
        revList.reverse()

        for i in range(len(revList)):
            if i != (len(revList) - 1):
                # temp solution til i deal with reparent with joints as they need special attention
                cmds.parent(nodes.nameFromMObject(revList[i].object()), nodes.nameFromMObject(revList[i + 1].object()))

        if rotationOrders:
            self.setRotationOrders(rotationOrders)

    def setParent(self, parent):
        p = nodes.nameFromMObject(parent)
        try:
            # temp solution til i deal with reparent with joints as they need special attention
            cmds.parent(nodes.nameFromMObject(self.joints[0].object()), p)
        except RuntimeError:
            return
            # nodes.setParent(self.joints[0].object(), parent)

    def setOrientations(self, orientations):
        for i in xrange(len(self.joints)):
            plugs.setAttr(om2.MFnDependencyNode(self.joints[i].object()).findPlug("jointOrient", False),
                          orientations[i])

    def setRotationOrders(self, orders):
        for x in xrange(len(self.joints)):
            plugs.setAttr(om2.MFnDependencyNode(self.joints[x].object()).findPlug("rotateOrder", False), orders[x])

    def setPreferredAngles(self, angles):
        for x in xrange(len(self.joints)):
            plugs.setAttr(om2.MFnDependencyNode(self.joints[x].object()).findPlug("preferredAngle", False), angles[x])


class FkChain(BoneChain):
    def __init__(self, joints=None):
        super(FkChain, self).__init__(joints)

        self.ctrls = []

    def create(self, shapes, names, positions, orientations, rotationOrders, skipLast=True):
        try:
            super(FkChain, self).create(names, positions, orientations, rotationOrders)
        except ValueError:
            logger.debug("Joints having already been created, skipping joint creation, moving to create Fk controls")

        for x in xrange(len(self.joints)):
            cntClass = control.Control(names[x])
            cntClass.create(shapes[x], om2.MVector(positions[x]), orientations[x], rotationOrder=rotationOrders[x])
            cntClass.addSrt("srt")
            self.ctrls.append(cntClass)

        revList = list(self.ctrls)
        revList.reverse()
        for i in range(len(revList)):
            if i != (len(revList) - 1):
                nodes.setParent(nodes.getParent(revList[i].mobject()), revList[i + 1].mobject(), True)

    def setParent(self, jointParent, ctrlParent):
        super(FkChain, self).setParent(jointParent)
        parenSrt = nodes.getParent(self.ctrls[0].mobject())
        nodes.setParent(parenSrt, ctrlParent, True)


class IkChain(BoneChain):
    def __init__(self, joints=None):
        super(IkChain, self).__init__(joints)

        self.ikCtrl = None
        self.upVector = None
        self.ikHandle = None

    def create(self, shape, names, positions, orientations, rotationOrders, skipLast=True):
        try:
            super(IkChain, self).create(names, positions, orientations, rotationOrders)
        except ValueError:
            logger.debug("Joints having already been created, skipping joint creation, moving to create Fk controls")

    def alignUpVector(self):
        pass
