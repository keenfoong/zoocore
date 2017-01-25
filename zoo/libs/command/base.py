import inspect
import os, sys
import traceback
import time

from zoo.libs.command import commandregistry
from collections import deque

from zoo.libs.utils import env


class ExecutorBase(object):
    def __init__(self):
        self.commands = {}
        self.undoStack = deque()

    def execute(self, name, **kwargs):
        command = self.findCommand(name)
        if command is None:
            raise ValueError("No command by the name -> {} exists within the registry!".format(name))
        command = command()
        command.prepareCommand()
        command.resolveArguments(kwargs)
        exc_tb = None
        exc_type = None
        exc_value = None
        try:
            command.stats = CommandStats(command)
            self.undoStack.append(command)
            result = self._callDoIt(command)
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            raise
        finally:
            tb = None
            if exc_type and exc_value and exc_tb:
                tb = traceback.format_exception(exc_type, exc_value, exc_tb)
            command.stats.finish(tb)

        return result

    def undoLast(self):
        if self.undoStack:
            command = self.undoStack[-1]
            if command is not None and command.isUndoable:
                command.undoIt()
                self.undoStack.remove(command)
                return True
        return False

    def registerCommand(self, clsobj):
        command = commandregistry.CommandRegistry().registerCommand(clsobj)
        if command is not None:
            self.commands[command.id] = command
            return True
        return False

    def registerEnv(self, env):
        environmentPaths = os.environ.get(env)
        if environmentPaths is None:
            raise ValueError("No environment variable with the name -> {} exists".format(env))
        environmentPaths = environmentPaths.split(os.pathsep)
        commands = commandregistry.CommandRegistry().registerCommands(environmentPaths)

        added = False
        for command in commands:
            if command.id not in self.commands:
                self.commands[command.id] = command
                added = True
        return added

    def findCommand(self, name):
        for command in iter(self.commands.values()):
            if command.id == name:
                return command

    def flush(self):
        self.undoStack.clear()

    def _callDoIt(self, command):
        return command.doIt(**command.arguments)


class CommandStats(object):
    def __init__(self, tool):
        self.command = tool
        self.startTime = 0.0
        self.endTime = 0.0
        self.executionTime = 0.0

        self.info = {}
        self._init()

    def _init(self):
        """Initializes some basic info about the plugin and the use environment
        Internal use only:
        """
        self.info.update({"id": self.command.id,
                          "creator": self.command.creator,
                          "module": self.command.__class__.__module__,
                          "filepath": inspect.getfile(self.command.__class__),
                          "application": env.application()
                          })
        self.info.update(env.machineInfo())

    def finish(self, tb=None):
        """Called when the plugin has finish executing
        """
        self.endTime = time.time()
        self.executionTime = self.endTime - self.startTime
        self.info["executionTime"] = self.executionTime
        self.info["lastUsed"] = self.endTime
        if tb:
            self.info["traceback"] = tb
