import math

from maya.api import OpenMaya as om2
from maya import OpenMaya as om1


def aimToNode(source, target, aimVector=None,
              upVector=None):
    eyeAim = aimVector or om2.MVector(1.0, 0.0, 0.0)
    eyeUp = upVector or om2.MVector(0.0, 1.0, 0.0)

    targetDag = om2.MFnDagNode(target).getPath()
    eyeDag = om2.MFnDagNode(source).getPath()

    transformFn = om2.MFnTransform(eyeDag)
    eyePivotPos = transformFn.rotatePivot(om2.MSpace.kWorld)

    transformFn.setObject(targetDag)
    targetPivotPos = transformFn.rotatePivot(om2.MSpace.kWorld)

    aimVector = targetPivotPos - eyePivotPos
    eyeU = aimVector.normal()
    worldUp = om1.MGlobal.upAxis()
    eyeW = (eyeU ^ om2.MVector(worldUp.x, worldUp.y, worldUp.z)).normal()
    eyeV = eyeW ^ eyeU
    quatU = om2.MQuaternion(eyeAim, eyeU)

    upRotated = eyeUp.rotateBy(quatU)

    angle = math.acos(upRotated * eyeV)

    quatV = om2.MQuaternion(angle, eyeU)

    if not eyeV.isEquivalent(upRotated.rotateBy(quatV), 1.0e-5):
        angle = (2 * math.pi) - angle
        quatV = om2.MQuaternion(angle, eyeU)

    quatU *= quatV
    # align the aim
    transformFn.setObject(eyeDag)
    transformFn.setRotation(quatU, om2.MSpace.kWorld)
