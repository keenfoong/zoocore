import os

import unittestBase
from zoo.libs.command import commandregistry
from testdata.commanddata import testcommands


class TestCommandRegistry(unittestBase.BaseUnitest):
    def setUp(self):
        self.registry = commandregistry

    def testRegisterCommand(self):
        result = self.registry.registerCommand(testcommands.TestCommandReg)
        self.assertIsNotNone(result)

    def testRegisterByModule(self):
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir,
                            "testdata", "commanddata", "testcommands.py"))
        commands = self.registry.registerByModule(path)
        self.assertTrue(len(commands) > 0)

    def testRegistryByDottedPath(self):
        path = "tests.testdata.commanddata.testcommands"
        commands = self.registry.registerByModule(path)
        self.assertTrue(len(commands) > 0)

    def testRegisterEnv(self):
        env = "ZOO_COMMAND_TEST"
        os.environ[env] = "tests.testdata.commanddata.testcommands"
        commands = self.registry.registryByEnv(env)
        self.assertTrue(len(commands) != 0)

    def testRegisterByPackage(self):
        env = "ZOO_COMMAND_TEST"
        os.environ[env] = "tests.testdata.commanddata"
        commands = self.registry.registryByEnv(env)
        self.assertTrue(len(commands) != 0)
