import os

from tests import mayatestutils
from tests.testdata import testmayacommand
from zoo.libs.command import executor


class TestMayaCommandExecutor(mayatestutils.BaseMayaTest):
    @classmethod
    def setUpClass(cls):
        super(TestMayaCommandExecutor, cls).setUpClass()
        os.environ["TESTDATA"] = "tests.testdata"

    def setUp(self):
        self.executor = executor.Executor()
        self.env = "TESTDATA"

        # def testRegisterCommand(self):
        #     self.executor.registerCommand(testmayacommand.TestCommandReg)
        #     self.assertTrue(len(self.executor.commands) > 0)
        #     self.assertIsNotNone(self.executor.findCommand("Test.TestCommand"))
        #
        # def testRegisterEnv(self):
        #     self.executor.registerEnv(self.env)
        #     self.assertTrue(len(self.executor.commands) > 0)
        #     self.assertIsNotNone(self.executor.findCommand("Test.TestCommand"))
        #
        # def testCommandExecutes(self):
        #     self.executor.registerEnv(self.env)
        #     result = self.executor.execute("Test.TestCommand", value="helloWorld")
        #     self.assertEquals(result, "helloWorld")
        #
        # def testCommandFailsArguments(self):
        #     self.executor.registerEnv(self.env)
        #     with self.assertRaises(ValueError) as context:
        #         self.executor.execute("Test.FailCommandArguments", value="helloWorld")
        #     self.assertTrue('Test.FailCommandArguments' in str(context.exception))
        #
        # def testUndoLast(self):
        #     self.executor.registerEnv(self.env)
        #     result = self.executor.execute("Test.TestCommandUndoable", value="helloWorld")
        #     self.assertEquals(result, "helloWorld")
        #     self.assertEquals(len(self.executor.undoStack), 1)
        #     result = self.executor.undoLast()
        #     self.assertTrue(result)
        #     self.assertEquals(len(self.executor.undoStack), 0)
        #     self.assertEquals(len(self.executor.redoStack), 1)
        #
        # def testUndoSkips(self):
        #     self.executor.registerEnv(self.env)
        #     result = self.executor.execute("Test.TestCommandNotUndoable", value="helloWorld")
        #     self.assertEquals(result, "helloWorld")
        #     self.assertEquals(len(self.executor.undoStack), 0)
        #     result = self.executor.undoLast()
        #     self.assertFalse(result)
        #
        # def testFlush(self):
        #     self.executor.registerEnv(self.env)
        #     result = self.executor.execute("Test.TestCommandUndoable", value="helloWorld")
        #     self.assertEquals(result, "helloWorld")
        #     self.assertEquals(len(self.executor.undoStack), 1)
        #     self.executor.flush()
        #     self.assertEquals(len(self.executor.undoStack), 0)
