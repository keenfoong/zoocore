from maya.api import OpenMaya as om2

from zoo.libs.utils import zlogging
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs

logger = zlogging.zooLogger


def poleVectorPosition(start, mid, end, multiplier=1.0):
    """This function gets the position of the polevector from 3 MVectors

    :param start: the start vector
    :type start: MVector
    :param mid: the mid vector
    :type mid: MVector
    :param end: the end vector
    :type end: MVector
    :return: the vector position of the pole vector
    :rtype: MVector
    """
    # calculate distance between
    startEnd = end - start
    startMid = mid - start
    dotP = startMid * startEnd

    try:
        proj = float(dotP) / float(startEnd.length())
    except ZeroDivisionError:
        logger.error("trying to divide by zero is unpredictable returning")
        raise ZeroDivisionError

    startEndN = startEnd.normal()
    projV = startEndN * proj
    arrowV = (startMid - projV) * multiplier
    finalV = arrowV + mid

    return finalV


def convertToNode(node, parent, prefix, nodeType="joint"):
    """Converts a node into a joint but does not delete the node ,
    transfers matrix over as well

    :param node: mobject, the node that will be converted
    :param parent: mobject to the transform to parent to
    :param prefix: str, the str value to give to the start of the node name
    :param nodeType: str, the node type to convert to. must be a dag type node
    :return: mObject, the mobject of the joint
    """
    mod = om2.DagModifier("createJoint")
    jnt = mod.createNode(nodeType)
    mod.doIt()
    nodes.rename(jnt, prefix + nodes.nameFromMObject(node, partialName=True))
    nodes.setParent(jnt, parent)
    plugs.setAttr(om2.MFnDagNode(jnt).findPlug("worldMatrix", False), nodes.getWorldMatrix(node))

    return jnt


def convertToSkeleton(rootNode, prefix="skel_", parentObj=None):
    """Converts a hierarchy of nodes into joints that have the same transform,
    with their name prefixed with the "prefix" arg.

    :param rootNode: PyNode , anything under this node gets converted.
    :param prefix: string, the name to add to the node name .
    :param parentObj:PyNode ,  the node to parent to skeleton to.
    :return:MObject
    """
    if parentObj is None:
        parentObj = nodes.getParent(rootNode)
    j = convertToNode(rootNode, parentObj, prefix)
    for c in nodes.getChildren(rootNode):
        convertToSkeleton(c, prefix, j)
    return j
