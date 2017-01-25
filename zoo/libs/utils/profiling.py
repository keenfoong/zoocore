import cProfile
import time
from zoo.libs.utils import zlogging
from functools import wraps

logger = zlogging.zooLogger


def profileit(name):
    """cProfile decorator to profile said function, must pass in a filename to write the information out to
    use RunSnakeRun to run the output

    :param name:
    :return:
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prof = cProfile.Profile()
            retval = prof.runcall(func, *args, **kwargs)
            # Note use of name from outer scope
            prof.dump_stats(name)
            return retval

        return wrapper

    return inner


def fnTimer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        logger.debug("Total time running {}: %s seconds".format(function.func_name, str(t1 - t0)))
        return result

    return function_timer
