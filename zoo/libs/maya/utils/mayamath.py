import math

from maya.api import OpenMaya as om2
from maya import OpenMaya as om1
from zoo.libs.utils import zoomath


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


def quaterionDot(qa, qb):
    return qa.w * qb.w + qa.x * qb.x + qa.y * qb.y + qa.z * qb.z


def slerp(qa, qb, weight):
    qc = om2.MQuaternion()
    dot = quaterionDot(qa, qb)
    if abs(dot >= 1.0):
        qc.w = qa.w
        qc.x = qa.x
        qc.y = qa.y
        qc.z = qa.z
        return qc
    halfTheta = math.acos(dot)
    sinhalfTheta = math.sqrt(1.0 - dot * dot)
    if zoomath.almostEqual(math.fabs(sinhalfTheta), 0.0, 2):
        qc.w = (qa.w * 0.5 + qb.w * 0.5)
        qc.x = (qa.x * 0.5 + qb.x * 0.5)
        qc.y = (qa.y * 0.5 + qb.y * 0.5)
        qc.z = (qa.z * 0.5 + qb.z * 0.5)
        return qc

    ratioA = math.sin((1.0 - weight) * halfTheta) / sinhalfTheta
    ratioB = math.sin(weight * halfTheta) / sinhalfTheta

    qc.w = (qa.w * ratioA + qb.w * ratioB)
    qc.x = (qa.x * ratioA + qb.x * ratioB)
    qc.y = (qa.y * ratioA + qb.y * ratioB)
    qc.z = (qa.z * ratioA + qb.z * ratioB)
    return qc
