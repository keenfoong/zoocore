import os

from maya import cmds
from maya.api import OpenMaya as om2
from zoo.libs.maya.api import nodes


def findAdditionalSceneDependencies(references=True, textures=True):
    """
    Find additional dependencies from the scene by looking at the file references and texture paths
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
    for file_node in cmds.ls(l=True, type="file"):
        # ensure this is actually part of this scene and not referenced
        if cmds.referenceQuery(file_node, isNodeReferenced=True):
            continue
        texture_path = os.path.abspath(cmds.getAttr(".".join([file_node, "fileTextureName"])))
        if texture_path:
            paths.add(texture_path)
    return paths


def findTextureNodePairs():
    paths = set()
    # now look at file texture nodes
    for file_node in cmds.ls(l=True, type="file"):
        # ensure this is actually part of this scene and not referenced
        if cmds.referenceQuery(file_node, isNodeReferenced=True):
            continue
        # get path and make it platform dependent
        texture_path = cmds.getAttr(os.path.normpath(".".join([file_node, "fileTextureName"])))
        if texture_path:
            paths.add(tuple(file_node, texture_path))
    return paths


def iterTextureNodePairs(includeReferences=False):
    for file_node in cmds.ls(l=True, type="file"):
        # ensure this is actually part of this scene and not referenced
        if includeReferences and cmds.referenceQuery(file_node, isNodeReferenced=True):
            continue
        # get path and make it platform dependent
        texture_path = cmds.getAttr(os.path.normpath(".".join([file_node, "fileTextureName"])))
        if texture_path:
            yield tuple([file_node, texture_path])


def findSceneReferences():
    paths = set()

    ref_nodes = cmds.ls(references=True)
    for ref_node in ref_nodes:
        fn = om2.MFnReference(nodes.asMObject(ref_node))
        path = os.path.abspath(fn.filename(True, True, False))
        if path:
            paths.add(path)
    return paths
