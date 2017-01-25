"""This module stores our Custom undo MPxCommand. Due to shit maya api undo support we're had to implement
our own that supports mel and API code. This MPx store's a list of zoo command which operate on the maya eg node creation.
When undo is called by maya or the user the MpxCommand loops over the stored zoo commands and calls undo.
However we only support what maya supports under the hood so we are limited to what maya gives us but it's more than
what we have out of the box. What this means is certain maya cmds and api class support undo and some do not
eg. MFnNurbsCurve.create() isn't a undoable at the core so we cannot support it.
We do support MDGModifier, MDagModifer, maya commands layer. See unittests for examples
"""
import sys

from maya.api import OpenMaya as om2

if not hasattr(om2, "_ZOOSTACK"):
    om2._ZOOCOMMAND = None
    om2._COMMANDEXECUTOR = None


def maya_useNewAPI():
    """WTF AutoDesk? Its existence tells maya that we are using api 2.0. seriously this should of just been a flag
    """
    pass


class UndoCmd(om2.MPxCommand):
    """Specialised MPxCommand to get around maya api retarded features.
    Stores zoo Commands on the UndoCmd
    """

    kCmdName = "zooAPIUndo"
    kId = "-id"
    kCallInfo = "-callInfo"

    def __init__(self):
        """We initialize a storage variable for a list of commands
        """
        om2.MPxCommand.__init__(self)
        self._command = None
        self._commandExecutor = None

    def doIt(self, argumentList):
        """Grab the list of current commands from the stack and dump it on our command so we can call undo

        :param argumentList: MArgList
        """
        # add the current queue into the mpxCommand instance then clean the queue since we dont need it anymore
        if om2._ZOOCOMMAND:
            self._command = om2._ZOOCOMMAND
            om2._ZOOCOMMAND = None
            self._commandExecutor = om2._COMMANDEXECUTOR

    def redoIt(self):
        """Runs the doit method on each of our stored commands
        """
        if self._command is None:
            return
        om2._COMMANDEXECUTOR._callDoIt(self._command)

    def undoIt(self):
        """Calls undoIt on each stored command in reverse order
        """
        if self._command is None:
            return
        if self.command.isUndoable:
            self.command.undoIt()
            om2._COMMANDEXECUTOR.undoStack.pop()

    def isUndoable(self):
        """True if we have stored commands
        :return: bool
        """
        return self.command.isUndoable

    @classmethod
    def cmdCreator(cls):
        return UndoCmd()

    @classmethod
    def syntaxCreator(cls):
        syntax = om2.MSyntax()
        # id - just for information and debugging
        syntax.addFlag(UndoCmd.kId, UndoCmd.kCallInfo, om2.MSyntax.kString)
        return syntax


def initializePlugin(mobject):
    mplugin = om2.MFnPlugin(mobject, "David Sparrow", "1.0", "Any")
    try:
        mplugin.registerCommand(UndoCmd.kCmdName, UndoCmd.cmdCreator, UndoCmd.syntaxCreator)
    except:
        sys.stderr.write('Failed to register command: ' + UndoCmd.kCmdName)


# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = om2.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(UndoCmd.kCmdName)
    except:
        sys.stderr.write('Failed to unregister command: %s' % UndoCmd.kCmdName)
