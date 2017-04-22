import inspect
import os
from abc import ABCMeta, abstractmethod, abstractproperty
from zoo.libs.command import errors


class CommandInterface(object):
    __metaclass__ = ABCMeta

    def __init__(self, stats=None):
        self.stats = stats
        self.arguments = {}
        self.initialize()

    def initialize(self):
        pass

    def undoIt(self):
        pass

    def resolveArguments(self, arguments):
        return {}

    @abstractmethod
    def doIt(self, **kwargs):
        pass

    @abstractproperty
    def id(self):
        pass

    @abstractproperty
    def creator(self):
        pass

    @abstractproperty
    def isUndoable(self):
        return False

    @staticmethod
    def uiData():
        return {"icon": "",
                "tooltip": "",
                "label": "",
                "color": "",
                "backgroundColor": ""
                }


class ZooCommand(CommandInterface):
    isEnabled = True

    def cancel(self, msg=None):
        raise errors.UserCancel(msg)

    def hasArgument(self, name):
        return name in self.arguments

    def _resolveArguments(self, arguments):
        kwargs = self.arguments
        unacceptedArgs = []
        for arg, value in iter(arguments.items()):
            if arg not in kwargs:
                unacceptedArgs.append(arg)
            kwargs[arg] = value
        if unacceptedArgs:
            raise ValueError("unaccepted arguments({}) for command -> {}".format(unacceptedArgs, self.id))
        results = self.resolveArguments(kwargs)
        kwargs.update(results)
        self.arguments = kwargs
        return True

    def _prepareCommand(self):
        funcArgs = inspect.getargspec(self.doIt)
        args = funcArgs.args[1:]
        defaults = funcArgs.defaults or tuple()
        if len(args) != len(defaults):
            raise ValueError("The command doIt function({}) must use keyword argwords".format(self.id))
        elif args and defaults:
            arguments = dict(zip(args, defaults))
            self.arguments = arguments
            return arguments
        return dict()

    def commandUi(self, uiType):
        # import locally due to avoid qt dependencies by default
        from zoo.libs.command import commandui
        if uiType == 0:
            commandui.CommandAction(self)


def generateCommandTemplate(className, id, doItContent, undoItContent, filePath,
                            creator, doitArgs):
    code = """
from zoo.libs.command import command


class {className}(command.ZooCommand):
    id = "{id}"
    creator = "{creator}"
    isUndoable = {isUndoable}
    isEnabled = True

    def doIt(self, {doItArgs}):
        {doItContent}
        
    def undoIt(self):
        {undoItContent}

""".format(className=className, id=id, isUndoable=True if undoItContent else False,
           doItArgs=", ".join(doitArgs), doItContent=doItContent or "pass",
           undoItContent=undoItContent or "pass", creator=creator)
    if os.path.exists(filePath):
        with open(filePath, "a") as f:
            f.write(code)
        return True
    with open(os.path.realpath(filePath), "w") as f:
        f.write(code)
    return True
