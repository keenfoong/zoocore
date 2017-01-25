import getpass
import platform
import os
import sys


def isInMaya():
    return "maya" in sys.executable.lower()


def application():
    if isInMaya():
        return "maya"
    # can extend this for other DCCs
    return "standalone"


def machineInfo():
    machineDict = {"pythonVersion": sys.version,
                   "node": platform.node(),
                   "OSRelease": platform.release(),
                   "OSVersion": platform.platform(),
                   "processor": platform.processor(),
                   "machineType": platform.machine(),
                   "env": os.environ,
                   "syspaths": sys.path}
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
