import subprocess
import platform
import argparse
import tempfile
import shutil
import os
import uuid
import errno
import stat
import logging

logger = logging.debug(__name__)


def getMayaLocation(mayaVersion):
    """Gets the generic maya location where maya is installed
    :param mayaVersion: int
    :return: str, the folder path to the maya install folder
    """
    location = os.environ.get("MAYA_LOCATION", "")
    if location:
        return location
    if platform.system() == "Windows":
        location = os.path.join("C:\\", "Program Files", "Autodesk", "Maya{}".format(mayaVersion))
    elif platform.system() == "Darwin":
        return os.path.join("/Applications", "Autodesk", "maya{0}".format(mayaVersion), "Maya.app", "Contents")
    else:
        location = os.path.join("usr", "autodesk", "maya{0}- x64".format(mayaVersion))
    logger.debug("Maya location: {}".format(location))
    return location


def mayapy(mayaVersion):
    """Returns the location of the mayapy exe path from the mayaversion
    :param mayaVersion: int, the maya version the workwith
    :return: the mayapy exe path
    """
    pyexe = os.path.join(getMayaLocation(mayaVersion), "bin", "mayapy")
    if platform.system() == "Windows":
        pyexe += ".exe"
    logger.debug("mayapy location %s" % pyexe)
    return pyexe


def createMayaPrefs(prefsDirectory):
    """Creates a temp directory and copys the clean preferences folder into this temp location. You need to manually cleanup
    :param prefsDirectory: str, the location of the maya preferences
    :return: str, the new location for the temp preferences
    """
    logger.debug("creating maya preferences")
    cleanPrefs = os.path.join(os.path.dirname(__file__), "cleanMayaPrefs")
    tmp = tempfile.gettempdir()
    if not os.path.exists(tmp):
        os.makedirs(tmp)
    destination = prefsDirectory if prefsDirectory else os.path.join(tmp, "mayaPrefsDir{}".format(str(uuid.uuid4())))
    if os.path.exists(destination):
        shutil.rmtree(destination, ignore_errors=False, onerror=removeReadOnly)
    # copy the prefs
    shutil.copytree(cleanPrefs, destination)
    logger.debug("created maya preferences at the follow location %s" %destination)
    return destination


def removeReadOnly(func, path, exc):
    """Called by shutil.rmtree when it encounters a readonly file.
    """
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise RuntimeError('Could not remove {0}'.format(path))


def main():
    """Entry function into running maya unittests, this setups the maya environment with clean preferences and runs
    the test via subprocess
    """
    import sys
    location = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.environ["PYTHONPATH"] = location
    sys.path.append(location)
    parser = argparse.ArgumentParser(description="Maya unittest runner")
    parser.add_argument("-a", "--application",
                        type=str,
                        default="standalone")
    parser.add_argument("-v", "--version",
                        help="Maya version",
                        type=int,
                        default=2017)

    args = parser.parse_args()
    if args.application == "maya":
        mayaLocation = mayapy(args.version)

        if not os.path.exists(mayaLocation):
            raise RuntimeError("maya location path doesn't exists -> %s" % mayaLocation)
        modulefile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mayatestutils.py")
        mayaprefs = createMayaPrefs(None)
        # maya prefs
        os.environ['MAYA_APP_DIR'] = mayaprefs
        cmd = [mayapy(args.version), modulefile]
    else:
        cmd = ["python", os.path.join(os.path.dirname(os.path.realpath(__file__)), "unittestBase.py")]
    try:
        logger.debug("Booting with cmd :: {}".format(cmd))
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        logger.error("hard crashed during unittests", exc_info=True)
    finally:
        # delete the temp preferences since we no longer need it
        if args.application == "maya":
            logger.debug("Removing mayaPreferenes")
            shutil.rmtree(mayaprefs)


if __name__ == '__main__':
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    main()
