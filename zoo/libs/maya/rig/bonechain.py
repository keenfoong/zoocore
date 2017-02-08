from maya.api import OpenMaya as om2
from maya import cmds

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs
from zoo.libs.maya.rig import control
from zoo.libs.utils import zlogging

logger = zlogging.getLogger(__name__)


class BoneChain(object):
    def __init__(self, joints):
        self.joints = joints or []

    def create(self, names, positions, orientations=None, rotationOrders=None):
        if self.joints:
            raise ValueError("Already created joints!")
        jointNames = []
        for i in xrange(len(positions)):
            cmds.select(cl=True)

            if orientations:
                tempJnt = cmds.joint(n=names[i], position=positions[i], orientation=orientations[i])

            else:
                tempJnt = cmds.joint(n=names[i], position=positions[i])

            self.joints.append(om2.MObjectHandle(nodes.asMObject(tempJnt)))
            jointNames.append(tempJnt)

        revList = list(self.joints)
        revList.reverse()

        for i in range(len(revList)):
            if i != (len(revList) - 1):
                nodes.setParent(revList[i].object(), revList[i + 1].object())

        if orientations:
            self.setOrientations(orientations)
        if rotationOrders:
            self.setRotationOrders(rotationOrders)

    def setParent(self, parent):
        nodes.setParent(self.joints[0].object(), parent)

    def setOrientations(self, orientations):
        for i in xrange(len(self.joints)):
            plugs.setAttr(om2.MFnDependencyNode(self.joints[i].object()).findPlug("jointOrient"), orientations[i])

    def setRotationOrders(self, orders):
        for x in xrange(len(self.joints)):
            plugs.setAttr(om2.MFnDependencyNode(self.joints[x].object()).findPlug("rotateOrder"), orders[x])

    def setPreferredAngles(self, angles):
        for x in xrange(len(self.joints)):
            plugs.setAttr(om2.MFnDependencyNode(self.joints[x].object()).findPlug("preferredAngle"), angles[x])


class FkChain(BoneChain):
    def __init__(self, joints):
        super(FkChain, self).__init__(joints)

        self.ctrls = []

    def create(self, shape, names, positions, orientations, rotationOrders, skipLast=True):
        try:
            super(FkChain, self).create(names, positions, orientations, rotationOrders)
        except ValueError:
            logger.debug("Joints having already been created, skipping joint creation, moving to create Fk controls")

        for x in xrange(len(self.joints)):
            cntClass = control.Control(names[x])
            cntClass.addSrt("srt")
            cntClass.create(shape, positions[x], orientations[x], rotationOrders[x])
            self.ctrls.append(cntClass)

        revList = list(self.ctrls)
        revList.reverse()
        for i in range(len(revList)):
            if i != (len(revList) - 1):
                nodes.setParent(nodes.getParent(revList[i].object()),revList[i + 1].mobject())


class IkChain(BoneChain):
    def __init__(self, joints):
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
