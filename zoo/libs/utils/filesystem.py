import os
import subprocess
import shutil
import errno
import zipfile
import cStringIO

from zoo.libs.utils import env
from zoo.libs.utils import zlogging

logger = zlogging.getLogger(__name__)


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


def copyDirectoy(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            logger.error("Failed to copy directory {} to destination: {}".format(src, dst), exc_info=True)
            raise


def zipwalk(zfilename):
    """Zip file tree generator.

    For each file entry in a zip archive, this yields
    a two tuple of the zip information and the data
    of the file as a StringIO object.

    zipinfo, filedata

    zipinfo is an instance of zipfile.ZipInfo class
    which gives information of the file contained
    in the zip archive. filedata is a StringIO instance
    representing the actual file data.

    If the file again a zip file, the generator extracts
    the contents of the zip file and walks them.

    Inspired by os.walk .
    """

    tempdir = os.environ.get('TEMP', os.environ.get('TMP', os.environ.get('TMPDIR', '/tmp')))

    try:
        z = zipfile.ZipFile(zfilename, "r")
        for info in z.infolist():
            fname = info.filename
            data = z.read(fname)

            if fname.endswith(".zip"):
                tmpfpath = os.path.join(tempdir, os.path.basename(fname))
                try:
                    open(tmpfpath, 'w+b').write(data)
                except (IOError, OSError):
                    logger.error("Failed to write file, {}".format(tmpfpath), exc_info=True)

                if zipfile.is_zipfile(tmpfpath):
                    try:
                        for x in zipwalk(tmpfpath):
                            yield x
                    except Exception:
                        logger.error("Failed", exc_info=True)
                        raise
                try:
                    os.remove(tmpfpath)
                except:
                    pass
            else:
                yield (info, cStringIO.StringIO(data))
    except (RuntimeError, zipfile.error):
        raise
