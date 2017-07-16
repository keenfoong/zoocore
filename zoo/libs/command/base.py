import inspect
import os
import sys
import time
import traceback
from collections import deque

from zoo.libs.command import commandregistry
from zoo.libs.command import errors
from zoo.libs.utils import env


class ExecutorBase(object):
    def __init__(self):
        self.commands = {}
        self.undoStack = deque()
        self.redoStack = deque()

    def execute(self, name, *args, **kwargs):
        command = self.findCommand(name)
        if command is None:
            raise ValueError("No command by the name -> {} exists within the registry!".format(name))
        command = command()
        command._prepareCommand()
        try:
            command._resolveArguments(kwargs)
        except errors.UserCancel:
            return
        except Exception:
            raise
        exc_tb = None
        exc_type = None
        exc_value = None
        result = None
        try:
            command.stats = CommandStats(command)
            result = self._callDoIt(command)
        except errors.UserCancel:
            self.undoStack.remove(command)
            command.stats.finish(None)
            return result
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            raise
        finally:
            tb = None

            if exc_type and exc_value and exc_tb:
                tb = traceback.format_exception(exc_type, exc_value, exc_tb)
            # do not add to our internal stack if we failed
            elif command.isUndoable:
                self.undoStack.append(command)
            command.stats.finish(tb)

        return result

    def undoLast(self):
        if self.undoStack:
            command = self.undoStack[-1]
            if command is not None and command.isUndoable:
                command.undoIt()
                self.redoStack.append(command)
                self.undoStack.remove(command)
                return True
        return False

    def redoLast(self):
        result = None
        if self.redoStack:
            command = self.redoStack.pop()
            if command is not None:
                exc_tb = None
                exc_type = None
                exc_value = None
                try:
                    command.stats = CommandStats(command)
                    result = self._callDoIt(command)
                except errors.UserCancel:
                    self.undoStack.remove(command)
                    command.stats.finish(None)
                    return
                except Exception:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_tb)
                    raise
                finally:
                    tb = None
                    if exc_type and exc_value and exc_tb:
                        tb = traceback.format_exception(exc_type, exc_value, exc_tb)
                    elif command.isUndoable:
                        self.undoStack.append(command)

                    command.stats.finish(tb)

        return result

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

    def findCommand(self, id):
        command = self.commands.get(id)
        if command is not None:
            return command

    def flush(self):
        self.undoStack.clear()
        self.redoStack.clear()

    def _callDoIt(self, command):
        return command.doIt(**command.arguments)

    def cancel(self, msg):
        raise errors.UserCancel(msg)

    def groups(self):
        groups = {}
        for c in self.commands:
            start = c.id.split(".")[0]
            if start in groups and c not in groups[start]:
                groups[start].append(c)
            elif start not in groups:
                groups[start] = [c]
        return groups


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
        try:
            path = inspect.getfile(self.command.__class__)
        except:
            path = ""

        self.info.update({"id": self.command.id,
                          "creator": self.command.creator,
                          "module": self.command.__class__.__module__,
                          "filepath": path,
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
