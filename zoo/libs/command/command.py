import inspect
from abc import ABCMeta, abstractmethod, abstractproperty


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
        pass

    def hasArgument(self, name):
        return name in self.arguments

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

    def _resolveArguments(self, arguments):
        kwargs = self.arguments
        unacceptedArgs = []
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

    def getUiWidget(self, uiType):
        # import locally due to qt dependencies
        from zoo.libs.command import commandui
        if uiType == 0:
            commandui.CommandAction(self)
