import os
import logging
import tempfile
import unittest
import shutil
from collections import OrderedDict

from zoo.libs.tooldata import tooldata
logger = logging.getLogger(__name__)


class TestToolData(unittest.TestCase):
    rootOne = ""
    rootTwo = ""
    rootThree = ""

    @classmethod
    def setUpClass(cls):
        cls.rootOne = tempfile.mkdtemp()
        cls.rootTwo = tempfile.mkdtemp()
        cls.rootThree = tempfile.mkdtemp()

    def setUp(self):
        self.toolset = tooldata.ToolSet()
        self.roots = OrderedDict({"internal": self.rootOne,
                                  "user": self.rootTwo,
                                  "network": self.rootThree})
        self.workspaceSetting = "prefs/hotkeys/workspace1"
        self.shaderEditorSetting = "prefs/tools/shaderEditor/uiState.json"

    def _bindRoots(self):
        for name, root in self.roots.items():
            self.toolset.addRoot(root, name)

    def test_addRoots(self):
        self._bindRoots()
        self.assertEquals(len(tooldata.ROOTS.keys()), 3)
        # check to make sure order is kept
        for i in range(3):
            rootKey = tooldata.ROOTS.keys()[i]
            self.assertTrue(rootKey, tooldata.ROOTS[rootKey])
        with self.assertRaises(tooldata.RootAlreadyExistsError):
            self.toolset.addRoot(tooldata.ROOTS["internal"], "internal")

    def test_createSetting(self):
        toolsSetting = self.toolset.createSetting(self.workspaceSetting, root="user",
                                                  data={"testdata": {"bob": "hello"}})
        self.assertEquals(toolsSetting.root, "user")
        self.assertTrue(os.path.exists(toolsSetting.path()))
        self.assertTrue((tooldata.ROOTS["user"] / self.workspaceSetting).exists())
        newSettings = toolsSetting.open(toolsSetting.root, toolsSetting.relativePath)
        self.assertEquals(newSettings["relativePath"], toolsSetting["relativePath"])
        self.assertEquals(newSettings["root"], toolsSetting["root"])
        self.assertEquals(newSettings["testdata"], {"bob": "hello"})

    @classmethod
    def tearDownClass(cls):
        for i in (cls.rootOne,
                  cls.rootTwo,
                  cls.rootThree):
            if os.path.exists(i):
                shutil.rmtree(i)
