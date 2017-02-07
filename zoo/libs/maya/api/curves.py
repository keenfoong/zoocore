from maya.api import OpenMaya as om2

from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import plugs


def getCurveData(shape):
    """From a given NurbsCurve shape node serialize the cvs positions, knots, degree, form rgb colours

    :param shape: MObject that represents the NurbsCurve shape
    :return: dict

    Example::
        >>>nurbsCurve = cmds.circle()[1]
        # requires an MObject of the shape node
        >>>data = curve_utils.getCurveData(api.asMObject(nurbsCurve))
    """
    if isinstance(shape, om2.MObject):
        shape = om2.MFnDagNode(shape).getPath()
    data = nodes.getNodeColourData(shape.node())
    curve = om2.MFnNurbsCurve(shape)
    knots = curve.knots()
    cvs = curve.cvPositions(om2.MSpace.kObject)
    data["knots"] = [i for i in knots]
    data["cvs"] = [(i.x, i.y, i.z) for i in cvs]
    data["degree"] = curve.degree
    data["form"] = curve.form
    return data


def createCurveShape(parent, data):
    """Create a specified nurbs curves based on the data

    :param parent: The transform that takes ownership of the shapes, if None is supplied then one will be created
    :type parent: MObject
    :param data: {"shapeName": {"cvs": [], "knots":[], "degree": int, "form": int}}
    :type data: dict
    :return: the parent node
    :rtype: MObject
    """
    if parent is None:
        parent = om2.MObject.kNullObj
    newCurve = om2.MFnNurbsCurve()
    created = []
    for shapeName, curveData in iter(data.items()):
        cvs = om2.MPointArray()
        for point in curveData["cvs"]:
            cvs.append(om2.MPoint(point))
        knots = curveData["knots"]
        degree = curveData["degree"]
        form = curveData["form"]
        enabled = curveData["overrideEnabled"]
        shape = newCurve.create(cvs, knots, degree, form, False, False, parent)
        if parent == om2.MObject.kNullObj and shape.apiType() == om2.MFn.kTransform:
            parent = shape
            shape = nodes.childPathAtIndex(om2.MFnDagNode(shape).getPath(), -1)
            shape = nodes.asMObject(shape)
        if enabled:
            plugs.setAttr(om2.MFnDependencyNode(shape).findPlug("overrideEnabled", False), int(curveData["overrideEnabled"]))
            colours = curveData["overrideColorRGB"]
            nodes.setNodeColour(newCurve.object(), colours)
        created.append(shape)
    return parent


def serializeCurve(node):
    """From a given transform serialize the shapes curve data and return a dict

    :param node: The MObject that represents the transform above the nurbsCurves
    :type node: MObject
    :return: returns the dict of data from the shapes
    :rtype: dict
    """
    shapes = nodes.shapes(om2.MFnDagNode(node).getPath())
    data = {}
    for shape in shapes:
        dag = om2.MFnDagNode(shape.node())
        isIntermediate = dag.isIntermediateObject
        if not isIntermediate:
            data[om2.MNamespace.stripNamespaceFromName(dag.name())] = getCurveData(shape)

    return data


def mirrorCurveCvs(curveObj, axis="x", space=None):
    """Mirrors the the curves transform shape cvs by a axis in a specified space

    :param curveObj: The curves transform to mirror
    :type curveObj: mobject
    :param axis: the axis the mirror on, accepts: 'x', 'y', 'z'
    :type axis: str
    :param space: the space to mirror by, accepts: MSpace.kObject, MSpace.kWorld, default: MSpace.kObject
    :type space: int
    Example::
            >>>nurbsCurve = cmds.circle()[0]
            >>>mirrorCurveCvs(api.asMObject(nurbsCurve), axis='y', space=om.MSpace.kObject)
    """
    space = space or om2.MSpace.kObject

    axis = axis.lower()
    axisDict = {'x': 0, 'y': 1, 'z': 2}
    axis = axisDict[axis]

    shapes = nodes.shapes(om2.MFnDagNode(curveObj).getPath())
    for shape in shapes:
        curve = om2.MFnNurbsCurve(shape)
        cvs = curve.getCVs(space=space)
        copyCvs = om2.MPointArray()
        # invert the cvs MPoints based on the axis
        for i in range(len(cvs)):
            pt = cvs[i]
            pt[axis] *= -1
            copyCvs.append(pt)

        curve.setCvPositions(copyCvs)
        curve.updateCurve()
