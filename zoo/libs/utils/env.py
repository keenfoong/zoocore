import getpass
import platform
import os
import sys


def isInMaya():
    return "maya" in sys.executable.lower()


def isMayapy():
    return "mayapy.exe" in sys.executable.lower()

def isIn3dsmax():
    return "3dsmax" in sys.executable.lower()


def isInMotionBuilder():
    return "motionbuilder" in sys.executable.lower()


def isInHoudini():
    return "houdini" in sys.executable.lower()


def application():
    if isInMaya():
        return "maya"
    elif isIn3dsmax():
        return "3dsmax"
    elif isInMotionBuilder():
        return "motionbuilder"
    elif isInHoudini():
        return "houdini"
    # can extend this for other DCCs
    return "standalone"


def machineInfo():
    """Returns basic information about the current pc that this code is running on
    :return:
                {'OSRelease': '7',
                 'OSVersion': 'Windows-7-6.1.7601-SP1',
                 'executable': 'C:\\Program Files\\Autodesk\\Maya2018\\bin\\maya.exe',
                 'machineType': 'AMD64',
                 'node': 'COMPUTERNAME',
                 'processor': 'Intel64 Family 6 Model 44 Stepping 2, GenuineIntel',
                 'pythonVersion': '2.7.11 (default, Jul  1 2016, 02:08:48) [MSC v.1900 64 bit (AMD64)]',
                 'syspaths': list(str),
                 'env': dict(os.environ)
                 }
    :rtype: dict
    """
    machineDict = {"pythonVersion": sys.version,
                   "node": platform.node(),
                   "OSRelease": platform.release(),
                   "OSVersion": platform.platform(),
                   "processor": platform.processor(),
                   "machineType": platform.machine(),
                   "env": os.environ,
                   "syspaths": sys.path,
                   "executable": sys.executable}
    return machineDict


def user():
    """
    :rtype: str
    """
    return getpass.getuser().lower()


def isMac():
    """
    :rtype: bool
    """
    plat = platform.system().lower()
    return plat.startswith('mac') or plat.startswith('os') or plat.startswith('darwin')


def isWindows():
    """
    :rtype: bool
    """
    return platform.system().lower().startswith('win')


def isLinux():
    """
    :rtype: bool
    """
    return platform.system().lower().startswith('lin')


def addToEnv(env, newPaths):
    # to cull empty strings or strings with spaces
    paths = [i for i in os.environ.get(env, "").split(os.pathsep) if i]

    for p in newPaths:
        if p not in paths:
            paths.append(p)
    os.environ[env] = os.pathsep.join(paths) + os.pathsep
