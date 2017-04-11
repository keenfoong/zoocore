from maya.api import OpenMaya as om2
from maya import cmds

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs
from zoo.libs.maya.api import constraints
from zoo.libs.maya.api import generic
from zoo.libs.maya.rig import control
from zoo.libs.maya.rig import skeletonutils
from zoo.libs.utils import zlogging
from zoo.libs.maya.utils import general
from zoo.libs.maya.utils import creation

logger = zlogging.getLogger(__name__)

general.loadPlugin("lookdevkit")


def dagDataIterator(data):
    for nodeData in iter(data):
        yield nodeData
        for i in nodeData.get("children", []):
            yield dagDataIterator(i)


class BoneChain(object):
    def __init__(self, joints=None, nameManager=None):
        """
        :param joints:
        :type joints:
        :param nameManager: Naming instance, we expect this to be already setup appropriately using the object expression
         we only change the type and area within this class, so any other tokens need to pre set.
        :type nameManager:
        """
        self.joints = joints or []
        self.nameManager = nameManager

    def create(self, data):
        """

        :param data: [{"name": "upr",
                      "position": [0.0,0.0,0.0],"rotation": [0.0,0.0,0.0],
                      "rotationOrder": 0, "shape": "circle"
                      }]
        :type data: list(dict)
        """
        if self.joints:
            raise ValueError("Already created joints!")
        for nodeData in iter(data):
            name = nodeData["name"]
            cmds.select(cl=True)
            if self.nameManager is not None:
                self.nameManager.overrideToken("section", name)
                self.nameManager.overrideToken("type", "joint")
                name = self.nameManager.resolve()
            tempJnt = cmds.joint(n=name, position=nodeData["position"], orientation=nodeData["rotation"])
            tempJnt = nodes.asMObject(tempJnt)
            plugs.setAttr(om2.MFnDependencyNode(tempJnt).findPlug("rotateOrder", False),
                          generic.intToMTransformRotationOrder(nodeData["rotationOrder"]))
            self.joints.append(om2.MObjectHandle(tempJnt))

        revList = list(self.joints)
        revList.reverse()

        for i in range(len(revList)):
            if i != (len(revList) - 1):
                # temp solution til i deal with reparent with joints as they need special attention
                cmds.parent(nodes.nameFromMObject(revList[i].object()), nodes.nameFromMObject(revList[i + 1].object()))

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
            plugs.setAttr(om2.MFnDependencyNode(self.joints[x].object()).findPlug("rotateOrder", False),
                          generic.intToMTransformRotationOrder(orders[x]))

    def setPreferredAngles(self, angles):
        for x in xrange(len(self.joints)):
            plugs.setAttr(om2.MFnDependencyNode(self.joints[x].object()).findPlug("preferredAngle", False), angles[x])


class FkChain(BoneChain):
    def __init__(self, joints=None, nameManager=None):
        super(FkChain, self).__init__(joints, nameManager=nameManager)

        self.ctrls = []
        self.extras = []
        if self.nameManager is not None:
            self.nameManager.overrideToken("system", "fk")

    def create(self, data):
        """
        :param data: [{"name": "upr",
                      "position": [0.0,0.0,0.0],"rotation": [0.0,0.0,0.0],
                      "rotationOrder": 0, "shape": "circle"
                      }]
        :type data: list(dict)
        """

        try:
            super(FkChain, self).create(data)
        except ValueError:
            logger.debug("Joints having already been created, skipping joint creation, moving to create Fk controls")
        index = 0
        for nodeData in iter(data):
            name = nodeData["name"]
            if self.nameManager is not None:
                self.nameManager.overrideToken("section", name)
                self.nameManager.overrideToken("type", "control")
                name = self.nameManager.resolve()
            cntClass = control.Control(name=name)
            cntClass.create(nodeData["shape"], om2.MVector(nodeData["position"]), nodeData["rotation"],
                            rotationOrder=nodeData["rotationOrder"])
            cntClass.addSrt("srt")
            nodes.showHideAttributes(cntClass.mobject(), ["visibility"])
            constraint = constraints.ParentConstraint()
            constraint.create(cntClass.mobject(), self.joints[index].object())

            self.ctrls.append(cntClass)
            self.extras.append(constraint.node)
            index += 1

        revList = list(self.ctrls)
        revList.reverse()
        for i in range(len(revList)):
            if i != (len(revList) - 1):
                nodes.setParent(nodes.getParent(revList[i].mobject()), revList[i + 1].mobject(), True)

    def setParent(self, jointParent, ctrlParent):
        super(FkChain, self).setParent(jointParent)
        parenSrt = nodes.getParent(self.ctrls[0].mobject())
        nodes.setParent(parenSrt, ctrlParent, True)

    def addStretch(self, lengthPlugs, initalLengthPlugs):

        for x in xrange(1, len(self.ctrls)):
            joint = om2.MFnDependencyNode(nodes.getParent(self.ctrls[x].mobject()))
            floatNode = creation.floatMath(lengthPlugs[x - 1], initalLengthPlugs[x - 1], 0,
                                           "_".join([joint.name(), "length_add"]))
            floatFn = om2.MFnDependencyNode(floatNode)
            plugs.connectPlugs(floatFn.findPlug("outFloat", False), joint.findPlug("translateX", False))
            self.extras.append(om2.MObjectHandle(floatNode))


class VChain(BoneChain):
    def __init__(self, joints=None, nameManager=None):
        super(VChain, self).__init__(joints, nameManager)

        self.ikCtrl = None
        self.upVector = None
        self.extras = {}
        if self.nameManager is not None:
            self.nameManager.overrideToken("system", "ik")

    def create(self, data):
        """


        :param data: the Data must have
        [{"name": "upr",
                      "position": [0.0,0.0,0.0],"rotation": [0.0,0.0,0.0],
                      "rotationOrder": 0, "shape": "circle"
                      },
                  "name":"arm"
                    "position": [0.0,0.0,0.0],
                    "rotation": [0.0,0.0,0.0],
                    "rotationOrder": 0,
                    "shape": "circle"},
                    "pvCtrl":{},
                    },
                ]
        :type data: list(dict)
        """

        newData = list()
        ikCtrlData = None
        pvCtrlData = None
        for d in data:
            if d["id"] == "end":
                ikCtrlData = d
            elif d["id"] == "upVec":
                pvCtrlData = d
                continue
            newData.append(d)
        try:
            super(VChain, self).create(newData)
        except ValueError:
            logger.debug("Joints having already been created, skipping joint creation, moving to create Fk controls")

        ikCtrlName = ikCtrlData["name"]
        ikpvCtrl = pvCtrlData["name"]
        handleName = str(ikCtrlName)
        pvPosition = om2.MVector(pvCtrlData.get("position", self.alignUpVector()))

        if self.nameManager is not None:
            self.nameManager.overrideToken("section", ikCtrlName)
            self.nameManager.overrideToken("type", "control")
            ikCtrlName = self.nameManager.resolve()
            self.nameManager.overrideToken("type", "ikHandle")
            handleName = self.nameManager.resolve()
            self.nameManager.overrideToken("section", ikpvCtrl)
            self.nameManager.overrideToken("type", "polevector")
            ikpvCtrl = self.nameManager.resolve()

        self.ikCtrl = control.Control(name=ikCtrlName)
        self.ikCtrl.create(ikCtrlData["shape"], om2.MVector(ikCtrlData["position"]), ikCtrlData["rotation"],
                           ikCtrlData.get("rotationOrder", (0.0, 0.0, 0.0)))
        self.ikCtrl.addSrt("srt")
        self.upVector = control.Control(name=ikpvCtrl)
        self.upVector.create(pvCtrlData["shape"], pvPosition, pvCtrlData["rotation"],
                             pvCtrlData.get("rotationOrder", generic.intToMTransformRotationOrder(0)))
        self.upVector.addSrt("srt")

        # @todo should we do this with the api?
        ikHandle, ikEffector = cmds.ikHandle(sj=nodes.nameFromMObject(self.joints[0].object()),
                                             ee=nodes.nameFromMObject(self.joints[-1].object()),
                                             solver="ikRPsolver", n=handleName)
        upVecConstraint = nodes.asMObject(
            cmds.poleVectorConstraint(self.upVector.dagPath.fullPathName(), ikHandle)[0])

        ikHandle = nodes.asMObject(ikHandle)
        nodes.setParent(ikHandle, self.ikCtrl.mobject(), True)
        plugs.setAttr(om2.MFnDependencyNode(ikHandle).findPlug("rotate", False), om2.MVector(0.0, 0.0, 0.0))
        self.extras["ikhandle"] = om2.MObjectHandle(ikHandle)
        self.extras["ikEffector"] = om2.MObjectHandle(nodes.asMObject(ikEffector))
        self.extras["upVectorConstraint"] = om2.MObjectHandle(upVecConstraint)

    def setParent(self, jointParent, ctrlParent):
        super(VChain, self).setParent(jointParent)
        nodes.setParent(self.ikCtrl.srt.object(), ctrlParent, True)
        nodes.setParent(self.upVector.srt.object(), ctrlParent, True)

    def alignUpVector(self):
        startPos = nodes.getTranslation(self.joints[0].object(), om2.MSpace.kWorld)
        midPos = nodes.getTranslation(self.joints[1].object(), om2.MSpace.kWorld)
        endPos = nodes.getTranslation(self.joints[2].object(), om2.MSpace.kWorld)
        pvPos = skeletonutils.poleVectorPosition(startPos, midPos, endPos, 2.0)
        if self.upVector is not None:
            self.upVector.setPosition(pvPos, space=om2.MSpace.kWorld, useParent=True)
        return pvPos

    def createIkStretch(self, name, controlPanel, constantsPanel, counterScale):
        ik = VChainStretch(self.joints[1].object(), self.joints[2].object(), self.ikCtrl.mobject(),
                           self.upVector.mobject(),
                           ikhandle=self.extras["ikhandle"].object(), name=name)
        # incoming connection plugs
        ik.counterScalePlug = counterScale

        ik.uprLengthPlug = controlPanel.findPlug("uprIkLength", False)
        ik.lwrLengthPlug = controlPanel.findPlug("lwrIkLength", False)
        ik.elbowLockPlug = controlPanel.findPlug("upVecLock", False)
        ik.stretchPlug = controlPanel.findPlug("stretchIk", False)
        ik.softPlug = controlPanel.findPlug("softIk", False)

        ik.constantzero = constantsPanel.findPlug("constant_zero", False)
        ik.constantone = constantsPanel.findPlug("constant_one", False)
        ik.constantnegOne = constantsPanel.findPlug("constant_negOne", False)
        ik.constantSoft = constantsPanel.findPlug("constant_soft", False)
        ik.totalLengthPlug = constantsPanel.findPlug("constant_totalInitLength", False)
        ik.uprInitialLengthPlug = constantsPanel.findPlug("constant_uprInitialLength", False)
        ik.lwrInitialLengthPlug = constantsPanel.findPlug("constant_lwrInitialLength", False)
        ik.constructNodes()
        return ik


class VChainStretch(object):
    # todo rethink this, could possible try serializing the node network to JSON and then load into the class for connections
    def __init__(self, midJoint, endJoint, endTransform, upVec, ikhandle, name):
        self.startTransform = om2.MObjectHandle(nodes.createDagNode("ikStretch_start_pos", "transform"))
        nodes.setMatrix(self.startTransform.object(), nodes.getWorldMatrix(nodes.getParent(midJoint)))
        # node initializers
        self.midJoint = midJoint
        self.endJoint = endJoint
        self.endTransform = endTransform
        self.upVec = upVec
        self.name = name
        self.ikhandle = ikhandle
        # incoming connection plugs
        self.counterScalePlug = None
        self.totalLengthPlug = None
        self.uprLengthPlug = None
        self.lwrLengthPlug = None
        self.elbowLockPlug = None
        self.stretchPlug = None
        self.softPlug = None
        # constant plugs
        self.constantzero = None
        self.constantone = None
        self.constantnegOne = None
        self.constantSoft = None
        self.uprInitialLengthPlug = None
        self.lwrInitialLengthPlug = None

        # created nodes
        self.totalDistanceNode = None
        self.uprDistanceNode = None
        self.lwrDistanceNode = None
        self.daSubNode = None
        self.xMinusDaNode = None
        self.divBySoftNode = None
        self.powENode = None
        self.oneMinuspowENode = None
        self.timeSoftNode = None
        self.plusDaNode = None
        self.daConditionSoftNode = None
        self.distdiffIkStretchSub = None
        self.stretchikHandleBlend = None
        self.stretchikHandleNeg = None
        self.distdiffStretch = None
        self.stretchBlendNode = None
        self.uprInitLengthMult = None
        self.lwrInitLengthMult = None
        self.uprLockBlendNode = None
        self.lwrLockBlendNode = None
        self.uprLengthMult = None
        self.lwrLengthMult = None

    def constructNodes(self):
        lockReverseNode = om2.MFnDependencyNode(nodes.createDGNode("_".join([self.name, "lock_rev"]), "reverse"))
        lockReverseOutPlug = lockReverseNode.findPlug("outputX", False)
        plugs.connectPlugs(self.elbowLockPlug, lockReverseNode.findPlug("inputX", False))
        # builder all the nodes for soft ik
        self.totalDistanceNode = creation.distanceBetween(self.startTransform.object(), self.endTransform,
                                                          "_".join([self.name, "totalDist"]))
        self.totalDistanceNode = om2.MFnDependencyNode(self.totalDistanceNode[0])

        currentTotalDistancePlug = self.totalDistanceNode.findPlug("distance", False)
        self.uprDistanceNode = creation.distanceBetween(self.startTransform.object(), self.upVec,
                                                        "_".join([self.name, "uprDist"]))
        self.uprDistanceNode = om2.MFnDependencyNode(self.uprDistanceNode[0])
        self.lwrDistanceNode = creation.distanceBetween(self.upVec, self.endTransform,
                                                        "_".join([self.name, "lwrDist"]))
        self.lwrDistanceNode = om2.MFnDependencyNode(self.lwrDistanceNode[0])
        self.daSubNode = om2.MFnDependencyNode(creation.floatMath(self.totalLengthPlug, self.softPlug,
                                                                  operation=1,
                                                                  name="_".join([self.name, "daSub"])))
        daOutPlug = self.daSubNode.findPlug("outFloat", False)
        self.xMinusDaNode = om2.MFnDependencyNode(creation.floatMath(currentTotalDistancePlug, daOutPlug,
                                                                     operation=1,
                                                                     name="_".join([self.name, "da", "xMinusSub"])))
        self.negxMinusNode = om2.MFnDependencyNode(creation.floatMath(self.xMinusDaNode.findPlug("outFloat", False),
                                                                      self.constantnegOne,
                                                                      operation=2,
                                                                      name="_".join(
                                                                          [self.name, "negate", "xMinusSub"])))

        self.divBySoftNode = om2.MFnDependencyNode(creation.floatMath(self.negxMinusNode.findPlug("outFloat", False),
                                                                      self.softPlug,
                                                                      operation=3,
                                                                      name="_".join([self.name, "divBySoftSub"])))
        self.powENode = om2.MFnDependencyNode(creation.floatMath(self.divBySoftNode.findPlug("outFloat", False),
                                                                 self.constantSoft,
                                                                 operation=6,
                                                                 name="_".join([self.name, "powESoftSub"])))
        self.oneMinuspowENode = om2.MFnDependencyNode(creation.floatMath(self.constantone,
                                                                         self.powENode.findPlug("outFloat", False),
                                                                         operation=1,
                                                                         name="_".join(
                                                                             [self.name, "oneMinuspowESoftSub"])))

        self.timeSoftNode = om2.MFnDependencyNode(creation.floatMath(self.oneMinuspowENode.findPlug("outFloat", False),
                                                                     self.softPlug,
                                                                     operation=2,
                                                                     name="_".join([self.name, "timeSoftSub"])))
        self.plusDaNode = om2.MFnDependencyNode(creation.floatMath(self.timeSoftNode.findPlug("outFloat", False),
                                                                   daOutPlug,
                                                                   operation=0,
                                                                   name="_".join([self.name, "plusDaSoftSub"])))
        self.daConditionSoftNode = om2.MFnDependencyNode(nodes.createDGNode("_".join([self.name, "daSoftCond"]),
                                                                            "condition"))
        plugs.setAttr(self.daConditionSoftNode.findPlug("operation", False), 5)
        plugs.connectPlugs(self.plusDaNode.findPlug("outFloat", False),
                           self.daConditionSoftNode.findPlug("colorIfTrueR", False))
        plugs.connectPlugs(currentTotalDistancePlug, self.daConditionSoftNode.findPlug("colorIfFalseR", False))
        plugs.connectPlugs(daOutPlug, self.daConditionSoftNode.findPlug("firstTerm", False))
        plugs.connectPlugs(currentTotalDistancePlug, self.daConditionSoftNode.findPlug("secondTerm", False))

        # ikhandle
        self.distdiffIkStretchSub = om2.MFnDependencyNode(
            creation.floatMath(self.daConditionSoftNode.findPlug("outColorR", False),
                               currentTotalDistancePlug,
                               operation=1,
                               name="_".join([self.name, "plusDsSoftSub"])))
        self.stretchikHandleBlend = om2.MFnDependencyNode(
            creation.blendTwoAttr(self.distdiffIkStretchSub.findPlug("outFloat", False),
                                  self.constantzero, self.stretchPlug,
                                  "_".join([self.name, "stretchikHandle", "Blend"])))
        ikHandleSourcePlug = self.stretchikHandleBlend.findPlug("output", False)
        #
        value = ikHandleSourcePlug.asFloat()
        if value > 0:
            self.stretchikHandleNeg = om2.MFnDependencyNode(
                creation.floatMath(ikHandleSourcePlug,
                                   self.constantnegOne,
                                   operation=2,
                                   name="_".join([self.name, "stretchikHandle", "Blend"])))

            plugs.connectPlugs(self.stretchikHandleNeg.findPlug("outFloat", False),
                               om2.MFnDependencyNode(self.ikhandle).findPlug("translateX", False))
        plugs.connectPlugs(ikHandleSourcePlug, om2.MFnDependencyNode(self.ikhandle).findPlug("translateX", False))
        # locking and uprlwr lengths
        self.distdiffStretch = om2.MFnDependencyNode(creation.floatMath(currentTotalDistancePlug,
                                                                        self.daConditionSoftNode.findPlug("outColorR",
                                                                                                          False),
                                                                        operation=3,
                                                                        name="_".join(
                                                                            [self.name, "distdiff_stretchDiv"]))
                                                     )
        self.stretchBlendNode = om2.MFnDependencyNode(creation.blendTwoAttr(self.constantone,
                                                                            self.distdiffStretch.findPlug("outFloat",
                                                                                                          False),
                                                                            blender=self.stretchPlug,
                                                                            name="_".join([self.name, "stretchBlend"])))

        self.uprInitLengthMult = om2.MFnDependencyNode(
            creation.floatMath(self.stretchBlendNode.findPlug("output", False),
                               self.uprInitialLengthPlug,
                               operation=2,
                               name="_".join([self.name, "uprInitLengthMult"])))
        self.lwrInitLengthMult = om2.MFnDependencyNode(
            creation.floatMath(self.stretchBlendNode.findPlug("output", False),
                               self.lwrInitialLengthPlug,
                               operation=2,
                               name="_".join([self.name, "lwrInitLengthMult"])))
        self.uprLockBlendNode = om2.MFnDependencyNode(
            creation.blendTwoAttr(self.uprDistanceNode.findPlug("distance", False),
                                  self.uprInitLengthMult.findPlug("outFloat", False),
                                  blender=lockReverseOutPlug,
                                  name="_".join([self.name, "uprLockBlend"])))
        self.lwrLockBlendNode = om2.MFnDependencyNode(
            creation.blendTwoAttr(self.lwrDistanceNode.findPlug("distance", False),
                                  self.lwrInitLengthMult.findPlug("outFloat", False),
                                  blender=lockReverseOutPlug,
                                  name="_".join([self.name, "lwrLockBlend"])))
        self.uprLengthMult = om2.MFnDependencyNode(creation.floatMath(self.uprLengthPlug,
                                                                      self.uprLockBlendNode.findPlug("output", False),
                                                                      operation=2,
                                                                      name="_".join([self.name, "uprLengthMult"])))
        self.lwrLengthMult = om2.MFnDependencyNode(creation.floatMath(self.lwrLengthPlug,
                                                                      self.lwrLockBlendNode.findPlug("output", False),
                                                                      operation=2,
                                                                      name="_".join([self.name, "lwrLengthMult"])))
        plugs.connectPlugs(self.uprLengthMult.findPlug("outFloat", False),
                           om2.MFnDependencyNode(self.midJoint).findPlug("translateX", False))
        plugs.connectPlugs(self.lwrLengthMult.findPlug("outFloat", False),
                           om2.MFnDependencyNode(self.endJoint).findPlug("translateX", False))


def blendChains(drivenChain, targetAChain, targetBChain, blendAttribute, rotInterpolation=None, includeScale=False):
    """Uses Pair blend nodes to blend translate rotation and scale attributes"""
    blendNodes = []
    rotInterpolation = 1 if rotInterpolation is None else rotInterpolation
    for i in xrange(len(drivenChain)):
        driven = om2.MFnDependencyNode(drivenChain[i])
        targetA = om2.MFnDependencyNode(targetAChain[i])
        targetB = om2.MFnDependencyNode(targetBChain[i])
        blendNode = creation.pairBlend("_".join([targetA.name(), targetB.name(), driven.name()]),
                                       targetA.findPlug("rotate", False), targetB.findPlug("rotate", False),
                                       targetA.findPlug("translate", False), targetB.findPlug("translate", False),
                                       blendAttribute, rotInterpolation)
        blendNodeFn = om2.MFnDependencyNode(blendNode)
        plugs.connectPlugs(blendNodeFn.findPlug("outRotate", False), driven.findPlug("rotate", False))
        plugs.connectPlugs(blendNodeFn.findPlug("outTranslate", False), driven.findPlug("translate", False))

        blendNodes.append(blendNode)
        if includeScale:
            blendNode = creation.pairBlend("_".join([targetA.name(), targetB.name(), driven.name()]),
                                           None, None,
                                           targetA.findPlug("scale", False), targetB.findPlug("scale", False),
                                           blendAttribute, rotInterpolation)
            blendNodes.append(blendNode)
    return blendNodes
