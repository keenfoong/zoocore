import os
import subprocess
from zoo.libs.utils import env


def upDirectory(path, depth=1):
    """Walks up the directory structure, use the depth argument to determine how many directories to walk

    :param path: the starting path to walk up
    :type path: str
    :param depth: how many directories to walk
    :type depth: int
    :return: the found directory
    :rtype: str
    """
    _cur_depth = 1
    while _cur_depth < depth:
        path = os.path.dirname(path)
        _cur_depth += 1
    return path


def iterParentPath(childPath):
    """Generator function that walks up directory structure starting at the childPath

    :param childPath: the starting path to walk up
    :type childPath: str
    :rtype: generator(str)
    """
    path = childPath
    while os.path.split(path)[1]:
        path = os.path.split(path)[0]
        yield path


def findParentDirectory(childPath, folder):
    """recursively walks the up the directory structure and returns the first instance of the folder

    :param childPath: the childpath to walk up
    :type childPath: str
    :param folder: the folder name to find.
    :type folder: str
    :return: the first instance of folder once found.
    :rtype: str
    """
    for p in iterParentPath(childPath):
        if os.path.split(p)[-1] == folder:
            return p


def openLocation(path):
    """Open the file explorer at the given path location.

    :type path: str
    """
    if env.isLinux():
        os.system('konqueror "%s"&' % path)
    elif env.isWindows():
        os.startfile('%s' % path)
    elif env.isMac():
        subprocess.call(['open', '-R', path])
