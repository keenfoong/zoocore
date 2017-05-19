from zoo.libs.utils import env
from zoo.libs.command import base


class ExecutorMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            if env.isInMaya():
                from zoo.libs.maya.mayacommand import mayaexecutor
                cls._instance = type.__call__(mayaexecutor.MayaExecutor, *args, **kwargs)
        else:
            cls._instance = type.__call__(base.ExecutorBase, *args, **kwargs)
        return cls._instance


class Executor(object):
    __metaclass__ = ExecutorMeta
