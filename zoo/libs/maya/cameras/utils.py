from maya.api import OpenMaya as om2
from zoo.libs.maya.api import nodes
from zoo.libs.maya.meta import metacamera


def createCamera(name, start, end, focalLength=35.000,
                         horizontalFilmAperture=1.682):
    # returns the camera transform
    camObj = nodes.createDagNode(name, "camera")
    camObj = [i for i in nodes.iterChildren(camObj, False, om2.MFn.kCamera)]
    # expectation that the camera was created an the transform was returned above
    # add the meta camera data
    meta = metacamera.MetaCamera(camObj[0])
    meta.focalLength = focalLength
    meta.horizontalFilmAperture = horizontalFilmAperture
    meta.shotName = name
    meta.startFrame = start
    meta.endFrame = end
    return meta
