from maya.api import OpenMaya as om2
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs


def distanceBetween(firstNode, secondNode, name):
    firstFn = om2.MFnDependencyNode(firstNode)
    secondFn = om2.MFnDependencyNode(secondNode)

    distanceBetweenNode = nodes.createDGNode(name, "distanceBetween")
    distFn = om2.MFnDependencyNode(distanceBetweenNode)
    plugs.connectPlugs(firstFn.findPlug("rotatePivotTranslate", False), distFn.findPlug("point1", False))
    plugs.connectPlugs(firstFn.findPlug("worldMatrix", False), distFn.findPlug("matrix1", False))
    plugs.connectPlugs(secondFn.findPlug("rotatePivotTranslate", False), distFn.findPlug("point2", False))
    plugs.connectPlugs(secondFn.findPlug("worldMatrix", False), distFn.findPlug("matrix2", False))

    return distanceBetweenNode


def multiplyDivide(input1, input2, operation, name):
    """
    :param input1:the node attribute to connect to the input1 value or use int for value
    :type input1: MPlug or MVector
    :param input2:the node attribute to connect to the input2 value or use int for value
    :type input2: MPlug or MVector
    :param operation : the int value for operation ,
                                    no operation = 0,
                                    multipy = 1,
                                    divide = 2,
                                    power = 3
    :type operation: int
    :return, the multiplyDivide node MObject
    :rtype: MObject
    """

    mult = om2.MFnDependencyNode(nodes.createDGNode(name, "multiplyDivide"))
    # assume connection type
    if isinstance(input1, om2.MPlug):
        plugs.connectPlugs(input1, mult.findPlug("input1", False))
    # plug set
    else:
        plugs.setAttr(mult.findPlug("input1", False), input1)
    if isinstance(input2, om2.MPlug):
        plugs.connectPlugs(input2, mult.findPlug("input2", False))
    else:
        plugs.setAttr(mult.findPlug("input2", False), input1)
    plugs.setAttr(mult.findPlug("operation", False), operation)

    return mult.object()


def blendColors(color1, color2, name, blender):
    blendFn = om2.MFnDependencyNode(nodes.createDGNode(name, "blendColors"))
    if isinstance(color1, om2.MPlug):
        plugs.connectPlugs(color1, blendFn.findPlug("color1", False))
    else:
        plugs.setAttr(blendFn.findPlug("color1", False), color1)
    if isinstance(color2, om2.MPlug):
        plugs.connectPlugs(color2, blendFn.findPlug("color2", False))
    else:
        plugs.setAttr(blendFn.findPlug("color2", False), color2)
    if isinstance(blender, om2.MPlug):
        plugs.connectPlugs(blender, blendFn.findPlug("blender", False))
    else:
        plugs.setAttr(blendFn.findPlug("blender", False), blender)
    return blendFn.object()


def floatMath(floatA, floatB, operation, name):
    floatMathFn = om2.MFnDependencyNode(nodes.createDGNode(name, "floatMath"))
    if isinstance(floatA, om2.MPlug):
        plugs.connectPlugs(floatA, floatMathFn.findPlug("floatA", False))
    else:
        plugs.setAttr(floatMathFn.findPlug("floatA", False), floatA)
    if isinstance(floatB, om2.MPlug):
        plugs.connectPlugs(floatA, floatMathFn.findPlug("floatB", False))
    else:
        plugs.setAttr(floatMathFn.findPlug("floatB", False), floatB)
    plugs.setAttr(floatMathFn.findPlug("operation", False), operation)
    return floatMathFn.object()


def blendTwoAttr(input1, input2, blender, name):
    fn = om2.MFnDependencyNode(nodes.createDGNode(name, "blendTwoAttr"))
    inputArray = fn.findPlug("input", False)
    plugs.connectPlugs(input1, inputArray.elementByLogicalIndex(-1))
    plugs.connectPlugs(input2, inputArray.elementByLogicalIndex(-1))
    plugs.connectPlugs(blender, fn.findPlug("attributeBlender", False))
    return fn.object()
