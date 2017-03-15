from zoo.libs.command import command


from zoo.libs.maya.api import nodes
from maya.api import OpenMaya as om2

class MayaTestCommand(command.ZooCommand):
    id="Test.mayaCommand"
    _testNode = None

    def doIt(self):
        print "inside command"
        node = nodes.createDagNode("testNode", "transform")
        self._testNode = om2.MObjectHandle(node)

    def undoIt(self):
        if self._testNode is None:
            raise ValueError("failed to undo")
        mod = om2.MDagModifier()
        mod.deleteNode(self._testNode.object())
        mod.doIt()
        self._testNode = None