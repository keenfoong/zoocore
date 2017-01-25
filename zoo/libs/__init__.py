# # import sys
# # sys.path.append(r"D:\tools\zootools2")
# # from zoo import startup
# # startup.startUp()
# from zoo.libs.maya.api import nodes
# from zoo.libs.maya.api import plugs
# from maya.api import OpenMaya as om2
#
# container = nodes.asMObject("arm_L_component")
# conNode = om2.MFnContainerNode(container)
# members = conNode.getMembers()
# componentData = {}
# lowerFirst = lambda s: s[:1].lower() + s[1:] if s else ''
# for i in members:
#
#     if i.hasFn(om2.MFn.kDagNode):
#         node = om2.MFnDagNode(i)
#         nodeName = node.fullPathName()
#         componentData[nodeName] = {"parent": om2.MFnDagNode(node.parent(0)).fullPathName(),
#                                    "transform": nodes.getWorldMatrix(i)}
#     else:
#         node = om2.MFnDependencyNode(i)
#         nodeName = node.name()
#         componentData[nodeName] = {}
#
#     componentData[nodeName] = {"name": nodeName,
#                                "type": lowerFirst(i.apiTypeStr[1:])}
#
#     connections = node.getConnections()
#     attributes = {}
#     for i in iter(connections):
#         if i.isDestination:
#             source = i.source()
#
#             attributes[i.name()] = {"name": i.name(),
#                                     "connection": (nodes.nameFromMObject(source.node()), source.name())}
#
#     componentData[nodeName].update({"attributes": attributes})
# import pprint
#
# pprint.pprint(componentData)
