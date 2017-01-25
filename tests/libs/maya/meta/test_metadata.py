from tests import mayatestutils

from zoo.libs.maya.meta import metadata
from zoo.libs.maya.api import nodes


class TestMetaData(mayatestutils.BaseMayaTest):
    def setUp(self):
        self.meta = metadata.MetaNode(name="testNode")

    def test_hasDefaultAttributes(self):
        self.assertTrue(self.meta.hasAttribute("root"))
        self.assertTrue(self.meta.hasAttribute("uuid"))
        self.assertTrue(self.meta.hasAttribute("metaParent"))
        self.assertTrue(self.meta.hasAttribute("metaChildren"))
        self.assertFalse(self.meta.findPlug("root", False).asBool())

    def test_setattr(self):
        self.meta.uuid = "testClass"
        self.assertEquals(self.meta.uuid.asString(), "testClass")
        with self.assertRaises(TypeError):
            self.meta.uuid = 10
        child = metadata.MetaNode()
        self.meta.metaParent = child
        self.assertIsNotNone(child.metaParent())
        self.assertIsNotNone(self.meta.metaChildren())

    def test_addChild(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = metadata.MetaNode(newNode)
        self.meta.addChild(newParent)
        self.assertEquals(len(self.meta.metaChildren()), 1)
        self.assertEquals(self.meta.metaChildren()[0].mobject(), newParent.mobject())

    def test_addParent(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = metadata.MetaNode(newNode)
        self.meta.addParent(newParent)
        self.assertEquals(self.meta.metaParent().mobject(), newParent.mobject())

    def test_removeChild(self):
        newNode = nodes.createDagNode("test", "transform")
        newParent = metadata.MetaNode(newNode)
        self.meta.addParent(newParent)
        self.assertEquals(len(newParent.metaChildren()), 1)
        newParent.removeChild(self.meta)
        self.assertEquals(len(newParent.metaChildren()), 0)
        self.meta.addParent(newParent)
        self.assertEquals(len(newParent.metaChildren()), 1)
        newParent.removeChild(self.meta.mobject())
        self.assertEquals(len(newParent.metaChildren()), 0)

    def test_iterMetaChildren(self):
        childOne = metadata.MetaNode(nodes.createDagNode("child", "transform"))
        childTwo = metadata.MetaNode(nodes.createDagNode("child1", "transform"))
        childThree = metadata.MetaNode(nodes.createDagNode("child2", "transform"))
        self.meta.addChild(childOne)
        childOne.addChild(childTwo)
        childTwo.addChild(childThree)
        iterchildren = [i for i in self.meta.iterMetaChildren()]
        nonChildren = [i for i in self.meta.iterMetaChildren(depthLimit=1)]
        self.assertEquals(len(nonChildren), 1)
        self.assertEquals(len(iterchildren), 3)
        selection = [childOne, childTwo, childThree]
        # non recursive
        self.assertTrue(nonChildren[0] in nonChildren)
        for i in selection:
            self.assertTrue(i in iterchildren)
            selection.remove(i)

    def test_iterMetaChildrenLargeNetwork(self):
        # large network
        children = []
        parentMeta = metadata.MetaNode(nodes.createDGNode("parentMeta", "network"))
        # to test connecting multiple nodes to a single parent
        for i in range(100):
            child = metadata.MetaNode(nodes.createDGNode("child{}".format(i), "network"))
            parentMeta.addChild(child)
            children.append(child)
        self.assertTrue(len(parentMeta.metaChildren()), len(children))

        parent = parentMeta
        for child in children:
            child.removeParent()
            child.addParent(parent)
            parent = child
        self.assertEquals(len([i for i in parentMeta.iterMetaChildren(depthLimit=1)]), 1)
        # we hit a depth limit
        self.assertEquals(len([i for i in parentMeta.iterMetaChildren(depthLimit=100)]), 100)
        self.assertEquals(len([i for i in parentMeta.iterMetaChildren(depthLimit=len(children) + 1)]),
                          len(children))
