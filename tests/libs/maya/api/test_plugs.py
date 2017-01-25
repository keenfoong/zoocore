from maya import cmds
from maya.api import OpenMaya as om2

from tests import mayatestutils
from zoo.libs.maya.api import plugs


class TestPlugs(mayatestutils.BaseMayaTest):
    application = "maya"

    def setUp(self):
        self.node = cmds.createNode("transform")

    def test_asMPlug(self):
        self.assertIsInstance(plugs.asMPlug(self.node + ".translate"), om2.MPlug)
        self.assertIsInstance(plugs.asMPlug(self.node + ".translateX"), om2.MPlug)
        self.assertIsInstance(plugs.asMPlug(self.node + ".worldMatrix[0]"), om2.MPlug)

    def test_isValidMPlug(self):
        obj = plugs.asMPlug(self.node + ".translate")
        self.assertTrue(plugs.isValidMPlug(obj))

    def test_connectPlugs(self):
        node = cmds.createNode("transform")
        plugSource = plugs.asMPlug(self.node + ".translate")
        plugdestination = plugs.asMPlug(node + ".translate")
        plugs.connectPlugs(plugSource, plugdestination)
        self.assertTrue(plugSource.isConnected)
        self.assertTrue(plugSource.isSource)
        self.assertTrue(plugdestination.isConnected)
        self.assertTrue(plugdestination.isDestination)
        connections = plugSource.connectedTo(False, True)
        self.assertTrue(connections[0] == plugdestination)
        self.assertEquals(plugdestination.connectedTo(True, False)[0].name(), plugSource.name())

    def test_iterChildren(self):
        translate = plugs.asMPlug(self.node + ".translate")
        worldMatrix = plugs.asMPlug(self.node + ".parentInverseMatrix")
        for i in plugs.iterChildren(translate):
            self.assertIsInstance(i, om2.MPlug)
        for i in plugs.iterChildren(worldMatrix):
            self.assertIsInstance(i, om2.MPlug)
