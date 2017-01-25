from tests import mayatestutils

from zoo.libs.maya.meta import base
from zoo.libs.maya.api import nodes
from zoo.libs.maya.api import attrtypes
from maya.api import OpenMaya as om2


class TestMetaData(mayatestutils.BaseMayaTest):
    def setUp(self):
        self.meta = base.MetaBase(name="testNode")

    def test_hasDefaultAttributes(self):
        self.assertTrue(self.meta.mfn().hasAttribute("mClass"))
        self.assertEquals(self.meta.mfn().findPlug("mClass", False).asString(), self.meta.__class__.__name__)

    def test_lockMetaManager(self):
        node = self.meta

        @base.lockMetaManager
        def test(node):
            self.assertFalse(node.mfn().isLocked)

        self.assertTrue(node.mfn().isLocked)
        test(node)
        self.assertTrue(node.mfn().isLocked)

    def test_renameAttribute(self):
        self.meta.renameAttribute("mClass", "bob")
        self.assertTrue(self.meta.mfn().hasAttribute("bob"))
        self.assertFalse(self.meta.mfn().hasAttribute("mClass"))

    def test_getAttribute(self):
        self.meta.addAttribute("test", 10.0, attrtypes.kMFnNumericDouble)
        self.assertIsNotNone(self.meta.getAttribute("test"))
        self.assertIsInstance(self.meta.getAttribute("test"), om2.MPlug)
        with self.assertRaises(AttributeError) as context:
            self.meta.testAttribute

    def test_name(self):
        self.assertEquals(self.meta.fullPathName(), "testNode")
        self.assertEquals(base.MetaBase(nodes.createDagNode("transform1", "transform")).fullPathName(), "|transform1")

    def test_delete(self):
        self.meta.delete()

    def testLock(self):
        self.assertTrue(self.meta.mfn().isLocked)
        self.meta.lock(False)
        self.assertFalse(self.meta.mfn().isLocked)

    def test_rename(self):
        self.meta.rename("newName")
        self.assertEquals(self.meta.fullPathName(), "newName")

    # def test_findPlugsByFilteredName(self):
    #     pass
    #
    # def test_findPlugsByType(self):
    #     pass
    #
    # def test_iterAttributes(self):
    #     pass
    #
    # def classNameFromPlug(node):
    #     pass
    #
    # def test_constructor(cls, *args, **kwargs):
    #     pass
    #
    # def test_equals(self, other):
    #     pass
    #
    # def test_metaClassPlug(self):
    #     pass
    #
    # def test_exists(self):
    #     pass
    #
    # def test_removeAttribute(self, name):
    #     pass
    #
    # def test_findConnectedNodes(self, attributeName="", filter=""):
    #     pass
    #
    # def test_serialize(self):
    #     pass
