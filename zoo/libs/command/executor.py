from zoo.libs.utils import env
from zoo.libs.command import base


class Executor(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if Executor._instance is None:
            if env.isInMaya():
                from zoo.libs.maya.mayacommand import mayaexecutor
                Executor._instance = mayaexecutor.MayaExecutor.__new__(*args, **kwargs)
            else:
                Executor._instance = base.ExecutorBase.__new__(*args, **kwargs)

        return Executor._instance
