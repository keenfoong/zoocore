import os

from maya import cmds
from maya.api import OpenMaya as om2


def findAdditionalSceneDependencies(references=True, textures=True):
    """Find additional dependencies from the scene by looking at the file references and texture paths
    """
    refPaths = set()
    if references:
        refPaths.union(findSceneTextures())
    if textures:
        refPaths.union(findSceneTextures())
    return refPaths


def findSceneTextures():
    paths = set()
    # now look at file texture nodes
    for file_node in cmds.ls(long=True, type="file"):
        dep = om2.MFnDependencyNode(file_node)
        # ensure this is actually part of this scene and not referenced
        if dep.isFromReferencedFile:
            continue
        texture_path = os.path.abspath(dep.findPlug("fileTextureName").asString())
        if texture_path:
            paths.add(texture_path)
    return paths


def findSceneReferences():
    paths = set()
    # first let's look at maya references
    for ref_node in cmds.ls(references=True):
        ref_path = os.path.abspath(cmds.referenceQuery(ref_node, filename=True))
        if ref_path:
            paths.add(ref_path)
    return paths
