import inspect
from abc import ABCMeta, abstractmethod, abstractproperty


class CommandInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def doIt(self, **kwargs):
        raise NotImplementedError("Subclasses should implement the doIt method")

    @abstractproperty
    def id(self):
        raise NotImplementedError("Subclasses should implement the doIt Propertie")


class ZooCommand(CommandInterface):
    id = None
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

    def hasArgument(self, name):
        return name in self.arguments

    def resolveArguments(self, arguments):
        kwargs = self.arguments
        unacceptedArgs = []
        for arg, value in iter(arguments.items()):
            if arg not in kwargs:
                unacceptedArgs.append(arg)
            kwargs[arg] = value
        if unacceptedArgs:
            raise ValueError("unaccepted arguments({}) for command -> {}".format(unacceptedArgs, self.id))
        self.arguments = kwargs

    def prepareCommand(self):
        funcArgs = inspect.getargspec(self.doIt)
        args = funcArgs.args[1:]
        defaults = funcArgs.defaults
        if not defaults:
            raise ValueError("The command doIt function({}) must use keyword argwords eg. value='hello'".format(
                self.id))

        if not args or not defaults:
            raise
        self.arguments = dict(zip(args, defaults))