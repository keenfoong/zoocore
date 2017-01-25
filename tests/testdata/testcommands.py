from zoo.libs.command import command


class TestCommandReg(command.ZooCommand):
    id = "Test.TestCommand"
    creator = "davidsp"
    isUndoable = False
    isEnabled = True

    def doIt(self, value="hello"):
        return value


class FailCommandArguments(command.ZooCommand):
    id = "Test.FailCommandArguments"
    creator = "davidsp"
    isUndoable = False
    isEnabled = True

    def doIt(self, value):
        pass


class TestCommandUndoable(command.ZooCommand):
    id = "Test.TestCommandUndoable"
    creator = "davidsp"
    isUndoable = True
    isEnabled = True
    value = ""

    def doIt(self, value="hello"):
        self.value = value
        return value

    def undoIt(self):
        self.value = ""


class TestCommandNotUndoable(command.ZooCommand):
    id = "Test.TestCommandNotUndoable"
    creator = "davidsp"
    isUndoable = False
    isEnabled = True
    value = ""

    def doIt(self, value="hello"):
        self.value = value
        return value

    def undoIt(self):
        self.value = ""
