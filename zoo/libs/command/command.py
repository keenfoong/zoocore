import inspect
from abc import ABCMeta, abstractmethod, abstractproperty


class CommandInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def doIt(self, **kwargs):
        raise NotImplementedError("Subclasses should implement the doIt method")

    @abstractproperty
    def id(self):
        raise NotImplementedError("Subclasses should implement the doIt Property")


class ZooCommand(CommandInterface):
    creator = ""
    isUndoable = False
    isEnabled = True

    def __init__(self):
        self.stats = None
        self.arguments = {}

    @classmethod
    def uiData(cls):
        return {"title": "",
                "icon": "",
                "tooltip": ""}

    def undoIt(self):
        pass

    def resolveArguments(self, arguments):
        pass

    def hasArgument(self, name):
        return name in self.arguments

    def _resolveArguments(self, arguments):
        kwargs = self.arguments
        unacceptedArgs = []
        print kwargs, arguments
        for arg, value in iter(arguments.items()):
            if arg not in kwargs:
                unacceptedArgs.append(arg)
            kwargs[arg] = value
        if unacceptedArgs:
            raise ValueError("unaccepted arguments({}) for command -> {}".format(unacceptedArgs, self.id))
        self.arguments = kwargs
        self.resolveArguments(kwargs)
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