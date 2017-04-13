import os
import subprocess
import shutil
import errno
import zipfile
import cStringIO
import re
from zoo.libs.utils import env
from zoo.libs.utils import zlogging

logger = zlogging.getLogger(__name__)

FILENAMEEXP = re.compile(u'[^\w\.-1]', re.UNICODE)


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
        os.system('konqueror "{}"&'.format(path))
    elif env.isWindows():
        os.startfile('{}'.format(path))
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


def folderSize(path):
    """Retrieves the total folder size in bytes
    :param path:
    :type path:
    :return: size in bytes
    :rtype: int
    """
    totalSize = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            totalSize += os.path.getsize(fp)
    return totalSize


def ensureFolderExists(path, permissions=0775, createPlaceHolderFile=False):
    """if the folder doesnt exist then one will be created.
    Function built due to version control mishaps with uncommited empty folders, this folder can generate
    a place holder file
    :param path: the folderpath to check or create
    :type path: str
    :param permissions: folder permissions mode
    :type permissions: int
    :param createPlaceHolderFile: if True create a placeholder text file
    :type createPlaceHolderFile: bool
    :raise OSError: raise OSError if the creation of the folder fails
    """
    if not os.path.exists(path):
        try:
            logger.debug("Creating folder {} [{}]".format(path, permissions))
            os.makedirs(path, permissions)
            if createPlaceHolderFile:
                placePath = os.path.join(path, "placeholder")
                if not os.path.exists(placePath):
                    with open(placePath, "wt") as fh:
                        fh.write("Automatically Generated placeHolder file.")
                        fh.write("The reason why this file exists is due to source control system's which do not "
                                 "handle empty folders.")

        except OSError, e:
            # more less work if network race conditions(joy!)
            if e.errno != errno.EEXIST:
                raise


def createValidfilename(name):
    """Sanitizer for file names which everyone tends to screw up, this function replace spaces and random character with
    underscore.
    Some random file name == Some_random_file_name
    :param name: the name to convert
    :type name: str
    :rtype: the same format as the passed argument type(utf8 etc)
    """
    value = name.strip()
    if isinstance(value, unicode):
        return FILENAMEEXP.sub("_", value)
    else:
        return FILENAMEEXP.sub("_", value.decode("utf-8")).encode("utf-8")


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
