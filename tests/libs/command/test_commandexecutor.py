import os

from tests import unittestBase
from zoo.libs.command import base
from tests.testdata import testcommands


class TestCommandExecutor(unittestBase.BaseUnitest):
    @classmethod
    def setUpClass(cls):
        super(TestCommandExecutor, cls).setUpClass()
        os.environ["TESTDATA"] = "tests.testdata"

    def setUp(self):
        self.executor = base.ExecutorBase()
        self.env = "TESTDATA"

    def testRegisterCommand(self):
        self.executor.registerCommand(testcommands.TestCommandReg)
        self.assertTrue(len(self.executor.commands) > 0)
        self.assertIsNotNone(self.executor.findCommand("test.testCommand"))

    def testRegisterEnv(self):
        self.executor.registerEnv(self.env)
        self.assertTrue(len(self.executor.commands) > 0)
        self.assertIsNotNone(self.executor.findCommand("test.testCommand"))

    def testCommandExecutes(self):
        self.executor.registerEnv(self.env)
        result = self.executor.execute("test.testCommand", value="helloWorld")
        self.assertEquals(result, "helloWorld")

    def testCommandFailsArguments(self):
        self.executor.registerEnv(self.env)
        with self.assertRaises(ValueError) as context:
            self.executor.execute("test.failCommandArguments", value="helloWorld")
        self.assertTrue('Test.FailCommandArguments' in str(context.exception))

    def testUndoLast(self):
        self.executor.registerEnv(self.env)
        result = self.executor.execute("test.testCommandUndoable", value="helloWorld")
        self.assertEquals(result, "helloWorld")
        self.assertEquals(len(self.executor.undoStack), 1)
        result = self.executor.undoLast()
        self.assertTrue(result)
        self.assertEquals(len(self.executor.undoStack), 0)
        self.assertEquals(len(self.executor.redoStack), 1)

    def testUndoSkips(self):
        self.executor.registerEnv(self.env)
        result = self.executor.execute("test.testCommandNotUndoable", value="helloWorld")
        self.assertEquals(result, "helloWorld")
        self.assertEquals(len(self.executor.undoStack), 0)
        result = self.executor.undoLast()
        self.assertFalse(result)

    def testFlush(self):
        self.executor.registerEnv(self.env)
        result = self.executor.execute("test.testCommandUndoable", value="helloWorld")
        self.assertEquals(result, "helloWorld")
        self.assertEquals(len(self.executor.undoStack), 1)
        self.executor.flush()
        self.assertEquals(len(self.executor.undoStack), 0)
