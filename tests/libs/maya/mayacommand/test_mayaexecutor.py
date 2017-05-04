import os
from maya import cmds
from tests import mayatestutils

from zoo.libs.command import executor


class TestMayaCommandExecutor(mayatestutils.BaseMayaTest):
    @classmethod
    def setUpClass(cls):
        super(TestMayaCommandExecutor, cls).setUpClass()
        os.environ["TESTDATA"] = "tests.testdata.mayacommanddata;tests.testdata.commanddata"

    def setUp(self):
        self.executor = executor.Executor()
        self.env = "TESTDATA"

    def testCommandExecutes(self):
        self.executor.registerEnv(self.env)
        result = self.executor.execute("Test.mayaSimpleCommand")
        self.assertEquals(result, "helloWorld")
        self.assertEquals(len(self.executor.undoStack), 1)
        self.assertEquals(cmds.undoInfo(l=True), 1)

    # standalone based commands need to be tested in maya as well
    def testCommandFailsArguments(self):
        self.executor.registerEnv(self.env)
        with self.assertRaises(ValueError) as context:
            self.executor.execute("Test.FailCommandArguments", value="helloWorld")
        self.assertTrue('Test.FailCommandArguments' in str(context.exception))
        self.assertEquals(len(self.executor.undoStack), 0)
        self.assertEquals(len(cmds.undoInfo), 0)

    def testUndoLast(self):
        self.executor.registerEnv(self.env)
        result = self.executor.execute("Test.TestCommandUndoable", value="helloWorld")
        self.assertEquals(result, "helloWorld")
        self.assertEquals(len(self.executor.undoStack), 1)
        self.assertEquals(len(cmds.undoInfo), 1)
        result = self.executor.undoLast()
        self.assertTrue(result)
        self.assertEquals(len(self.executor.undoStack), 0)
        self.assertEquals(len(cmds.undoInfo), 0)
        self.assertEquals(len(self.executor.redoStack), 1)

    def testUndoSkips(self):
        self.executor.registerEnv(self.env)
        result = self.executor.execute("Test.TestCommandNotUndoable", value="helloWorld")
        self.assertEquals(result, "helloWorld")
        self.assertEquals(len(self.executor.undoStack), 0)
        self.assertEquals(len(cmds.undoInfo), 0)
        result = self.executor.undoLast()
        self.assertFalse(result)

    def testFlush(self):
        self.executor.registerEnv(self.env)
        result = self.executor.execute("Test.TestCommandUndoable", value="helloWorld")
        self.assertEquals(result, "helloWorld")
        self.assertEquals(len(self.executor.undoStack), 1)
        self.executor.flush()
        self.assertEquals(len(self.executor.undoStack), 0)
