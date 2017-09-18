from maya.api import OpenMaya as om2
from maya import cmds

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs
from zoo.libs.maya.api import generic
from zoo.libs.maya.api import attrtypes
from zoo.libs.maya.utils import creation


class BaseConstraint(object):
    def __init__(self, node=None, name=None):
        self.name = name
        if node is not None:
            self.node = om2.MObjectHandle(node)
        self._mfn = None

    def mobject(self):
        return self.node.object()

    @property
    def mfn(self):
        if self._mfn is not None:
            return self._mfn
        if self.node is None:
            raise ValueError("Must inialize the class with the constaint mobject or call create()")
        self._mfn = om2.MFnDependencyNode(self.node.object())
        return self._mfn

    def drivenObject(self):
        plug = self.mfn.findPlug("constraintParentInverseMatrix", False)
        if plug.isDestination:
            return plug.source().node()

    def driverObjects(self):
        plug = self.mfn.findPlug("target", False)
        targets = []
        for i in xrange(plug.evaluateNumElements()):
            targetElement = plug.elementByPhysicalIndex(i)
            for element in xrange(targetElement.numChildren()):
                child = targetElement.child(element)
                if child.isDestination:
                    targets.append(child.source().node())
                    break
        return targets

    def numTargets(self):
        mfn = self.mfn
        return mfn.findPlug("target", False).evaluateNumElements()


class ParentConstraint(BaseConstraint):
    def create(self, driver, driven, skipRotate=None, skipTranslate=None, maintainOffset=False):
        driverName = nodes.nameFromMObject(driver)
        drivenName = nodes.nameFromMObject(driven)

        const = cmds.parentConstraint(driverName, drivenName, skipRotate=skipRotate or [],
                                      skipTranslate=skipTranslate or [],
                                      weight=1.0, maintainOffset=maintainOffset)
        self.node = om2.MObjectHandle(nodes.asMObject(const[0]))
        return self.node.object()

    def addTarget(self, driver):
        """Adds the given driver transform to the constraint
        :param driver: The driver mobject transform
        :type driver: MObject
        @note having to use maya commands here due to api not able to resize the plugs array outside the datablock
        """
        driven = self.drivenObject()
        driverName = nodes.nameFromMObject(driver)  # so we have the fullPath
        driverShortName = om2.MNamespace.stripNamespaceFromName(driverName).split("|")[-1]
        nextWeightIndex = self.numTargets()  # starts at zero so the return is the next element
        drivenFn = om2.MFnDependencyNode(driven)
        offsetMatrix = om2.MTransformationMatrix(nodes.getOffsetMatrix(driver, driven))
        translation = offsetMatrix.translation(om2.MSpace.kTransform)
        rotation = generic.eulerToDegrees(
            offsetMatrix.rotation().reorder(plugs.getPlugValue(drivenFn.findPlug("rotateOrder", False))))
        # create the weight attribute
        weightName = "W".join([driverShortName, str(nextWeightIndex)])
        weightAttr = nodes.addAttribute(self.node.object(), weightName, weightName,
                                        attrType=attrtypes.kMFnNumericDouble)
        weightAttr.setMin(0.0)
        weightAttr.setMax(1.0)
        weightAttr.default = 1.0
        weightAttr.keyable = True
        driverFn = om2.MFnDependencyNode(driver)
        targetPlug = self.mfn.findPlug("target", False).elementByLogicalIndex(nextWeightIndex)
        cmds.connectAttr(driverFn.findPlug("parentMatrix", False).elementByPhysicalIndex(0).name(),
                         targetPlug.child(0).name())  # targetParentMatrix
        cmds.connectAttr(driverFn.findPlug("scale", False).name(), targetPlug.child(13).name())  # targetScale
        cmds.connectAttr(driverFn.findPlug("rotateOrder", False).name(),
                         targetPlug.child(8).name())  # targetRotateOrder
        cmds.connectAttr(driverFn.findPlug("rotate", False).name(), targetPlug.child(7).name())  # targetRotate
        cmds.connectAttr(driverFn.findPlug("rotatePivotTranslate", False).name(),
                         targetPlug.child(5).name())  # targetRotateTranslate
        cmds.connectAttr(driverFn.findPlug("rotatePivot", False).name(),
                         targetPlug.child(4).name())  # targetRotatePivot
        cmds.connectAttr(driverFn.findPlug("translate", False).name(), targetPlug.child(3).name())  # targetTranslate
        cmds.connectAttr(om2.MPlug(self.mfn.object(), weightAttr.object()).name(),
                         targetPlug.child(1).name())  # targetWeight
        # setting offset value
        plugs.setPlugValue(targetPlug.child(6), translation)  # targetOffsetTranslate
        plugs.setPlugValue(targetPlug.child(10), rotation)  # targetOffsetRotate


class MatrixConstraint(BaseConstraint):
    # @todo optimize parentInverse matrix by reconnecting to driven parent
    # @todo blending when needed
    # @todo rediscovery of nodes
    # @todo find drivers

    def drivenObject(self):
        pass

    def driverObjects(self):
        pass

    def create(self, driver, driven, skipScale=None, skipRotate=None, skipTranslate=None, maintainOffset=False):
        composename = "_".join([self.name, "wMtxCompose"])

        decompose = creation.createDecompose(composename, destination=driven,
                                             translateValues=skipTranslate,
                                             scaleValues=skipScale, rotationValues=skipRotate)
        decomposeFn = om2.MFnDependencyNode(decompose)

        if maintainOffset:
            offsetname = "_".join([self.name, "wMtxOffset"])
            offset = nodes.getOffsetMatrix(driver, driven)
            creation.createMultMatrix(offsetname,
                                      inputs=(offset, nodes.worldMatrixPlug(driver),
                                              nodes.parentInverseMatrixPlug(driven)),
                                      output=decomposeFn.findPlug("inputMatrix", False))

        else:
            plugs.connectPlugs(nodes.worldMatrixPlug(driver), decomposeFn.findPlug("inputMatrix", False))
        self.node = om2.MObjectHandle(decompose)
        return decompose
