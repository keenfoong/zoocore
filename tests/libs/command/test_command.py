from tests import unittestBase
from zoo.libs.command import command


class TestZooCommand(command.ZooCommand):
    id = "helloWorld"
    creator = "davidsp"
    isUndoable = False
    isEnabled = True

    def doIt(self):
        return "helloWorld"


class TestCommand(unittestBase.BaseUnitest):
    def setUp(self):
        self.command = TestZooCommand()

    def testPrepareCommand(self):
        pass

    def testResolveArguments(self):
        pass
