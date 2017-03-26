import traceback

import sys
from maya import cmds
from maya.api import OpenMaya as om2
from zoo.libs.command import base


class MayaExecutor(base.ExecutorBase):
    def __init__(self):
        super(MayaExecutor, self).__init__()
        self.undoStack = om2._ZOOCOMMAND
        om2._COMMANDEXECUTOR = self

    def execute(self, commandName, **kwargs):
        command = self.findCommand(commandName)
        if command is None:
            raise ValueError("No command by the name -> {} exists within the registry!".format(commandName))
        command = command()
        command.prepareCommand()
        if not command.isEnabled:
            raise
        exc_tb = None
        exc_type = None
        exc_value = None
        command.resolveArguments(kwargs)
        try:
            command.stats = base.CommandStats(command)
            cmds.undoInfo(openChunk=True)
            result = self._callDoIt(command)
            self.undoStack.append(command)
            om2._ZOOCOMMAND = command
            cmds.zooAPIUndo(id=command.id)
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            raise
        finally:
            tb = None
            if exc_type and exc_value and exc_tb:
                tb = traceback.format_exception(exc_type, exc_value, exc_tb)
            command.stats.finish(tb)

            cmds.undoInfo(closeChunk=True)

        return result

    def undoLast(self):
        cmds.undo()


