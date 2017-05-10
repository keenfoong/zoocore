import os

from maya import cmds


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


def findSceneReferences():
    paths = set()

    # first let's look at maya references
    ref_nodes = cmds.ls(references=True)
    for ref_node in ref_nodes:
        # get the path:
        ref_path = cmds.referenceQuery(ref_node, filename=True)
        if ref_path:
            paths.add(os.path.realpath(ref_path))
    return paths
