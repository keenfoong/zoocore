import contextlib
import json
import os
import subprocess
import shutil
import errno
import zipfile
import cStringIO
import re
import functools
import sys

from zoo.libs.utils import zlogging, commandline

logger = zlogging.getLogger(zlogging.CENTRAL_LOGGER_NAME)

FILENAMEEXP = re.compile(u'[^\w\.-1]', re.UNICODE)


def clearUnMasked(func):
    """Decorator which clears the umask for a method.
    The umask is a permissions mask that gets applied
    whenever new files or folders are created. For I/O methods
    that have a permissions parameter, it is important that the
    umask is cleared prior to execution, otherwise the default
    umask may alter the resulting permissions

    :type func: function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # set umask to zero, store old umask
        oldMask = os.umask(0)
        try:
            # execute method payload
            return func(*args, **kwargs)
        finally:
            # set mask back to previous value
            os.umask(oldMask)

    return wrapper


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
    """Opens the parent directory of a file, selecting the file if possible.

    *Note: needs to be tested in win 10 from inside of Maya, current issues

    :param path: the path to the directory or file
    :type path: str
    """
    platform = sys.platform
    if platform == 'win32':
        if os.path.isdir(path):
            subprocess.Popen(["explorer", os.path.dirname(path)], shell=True)
            return
        subprocess.Popen(["explorer", "/select", path], shell=True)
    elif platform == 'darwin':
        if os.path.isdir(path):
            subprocess.Popen(["explorer", os.path.dirname(path)])
            return
        subprocess.Popen(["open" "-R", os.path.dirname(path)])
    else:
        subprocess.Popen(["xdg-open", os.path.dirname(path)])


def openDirectory(directoryPath):
    """Opens the native OS folder to the directory of file name
    similar to os.startfile(filename) but also supporting osx and linux

    *Note: current duplicate of findParentDirectory() Just it is not working from Maya, needs to be fixed
    :param directoryPath: the path to the directory to open
    :type directoryPath: str
    """
    # TODO:  Note: This function is a current duplicate of findParentDirectory()
    # TODO: findParentDirectory() is not working from Maya, needs to be sorted
    if sys.platform == "win32":
        os.startfile(directoryPath)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, directoryPath])


@clearUnMasked
def copyFile(src, dst, permissions=0666):
    """Copy file and sets its permissions.

    :param src: Source file
    :param dst: destination 
    :param permissions: Permissions to use for target file. Default permissions will \
                        be readable and writable for all users.
    """
    dirname = os.path.dirname(dst)
    if not os.path.isdir(dirname):
        old_umask = os.umask(0)
        os.makedirs(dirname, permissions)
        os.umask(old_umask)
    shutil.copy(src, dst)
    # os.chmod(dst, permissions)


def batchCopyFiles(paths, permissions=0777):
    """ Expects the parent folder to have been already created.

    :param paths: source path, destination path
    :type paths: tuple(tuple(str, str))
    :param permissions: OS permissions
    :type permissions: int
    :return: a list of tuples containing source,destination fails
    :rtype: list(tuple(str, str)
    """
    failed = []
    for source, destination in paths:
        try:
            logger.info("Copying %s --> %s..." % (source, destination))
            copy_file(source, destination, permissions=permissions)
        except OSError:
            raise
            failed.append((source, destination))
            continue
    return failed


def copyDirectoy(src, dst, ignorePattern=None):
    """Copies the directory tree using shutil.copytree

    :param src: the Source directory to copy.
    :type src: str
    :param dst: the destination directory.
    :type dst: str
    :raise: OSError
    """
    try:
        if ignorePattern:
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*ignorePattern))
            return
        shutil.copytree(src, dst)

    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            logger.error("Failed to copy directory {} to destination: {}".format(src, dst), exc_info=True)
            raise


class MoveFileContext(object):
    """With context utility to ensures that files that were moved within the scope are moved to their
    original location if an exception was raised during that scope.

    .. code-block:: python

        with MoveFileContext() as FileContext:
            someSourcePath = os.path.expandUser("~/soemfile.config")
                FileContext.move(sourceSourcePath, os.path.join(os.path.dirname(sourcePath), "destination.config"))
                ValueError("raise an error so we revert")

    """

    def __init__(self):
        self._stack = []

    def __enter__(self):
        """Returns the current class instance
        """
        return self

    def move(self, source, destination):
        """Move's a file and keeps track of the source/destination if it succeeded.

        :param source: Source file to move.
        :param destination: New location for that file.
        """
        shutil.move(source, destination)
        self._stack.append((source, destination))

    def __exit__(self, ex_type, value, traceback):
        """
        If some files have been moved, move them back to their original location.
        """
        if (ex_type or value or traceback) and self._stack:
            logger.debug("Reverting file move changes!")
            # Move files back to their original location.
            for source, destination in self._stack:
                logger.debug("Moving {} -> {}".format(destination, source))
                shutil.move(destination, source)


def folderSize(path):
    """Retrieves the total folder size in bytes

    :param path: Returns the total folder size by walking the directory adding together all child files sizes.
    :type path: str
    :return: size in bytes
    :rtype: int
    """
    totalSize = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            totalSize += os.path.getsize(fp)
    return totalSize


def ensureFolderExists(path, permissions=0775, placeHolder=False):
    """if the folder doesnt exist then one will be created.
    Function built due to version control mishaps with uncommited empty folders, this folder can generate
    a place holder file.

    :param path: the folderpath to check or create
    :type path: str
    :param permissions: folder permissions mode
    :type permissions: int
    :param placeHolder: if True create a placeholder text file
    :type placeHolder: bool
    :raise OSError: raise OSError if the creation of the folder fails
    """
    if not os.path.exists(path):
        try:
            logger.debug("Creating folder {} [{}]".format(path, permissions))
            os.makedirs(path, permissions)
            if placeHolder:
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

    .. code-block:: python

        createValidFilename("Some random file name")
        #result: "Some_random_file_name"

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


def directoryTreeToDict(path):
    d = {'name': os.path.basename(path),
         "path": path}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [directoryTreeToDict(os.path.join(path, x)) for x in os.listdir(path)]
    else:
        d['type'] = "file"
    return d


if os.name == "nt" and sys.version_info[0] < 3:
    def symlink_ms(source, linkname):
        """Python 2 doesn't have os.symlink on windows so we do it ourselfs
        
        :param source: sourceFile
        :type source: str
        :param linkname: symlink path
        :type linkname: str
        :raises: WindowsError, raises when it fails to create the symlink if the user permissions \
         are incorrect
        """
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        try:
            if csl(linkname, source.replace('/', '\\'), flags) == 0:
                raise ctypes.WinError()
        except WindowsError:
            raise WindowsError("Failed to create symbolicLink due to user permissions")


    os.symlink = symlink_ms


def loadJson(filePath):
    """
    This procedure loads and returns the data of a json file

    :return type{dict}: the content of the file
    """
    # load our file
    try:
        with loadFile(filePath) as f:
            data = json.load(f)
    except Exception as er:
        logger.debug("file (%s) not loaded" % filePath)
        raise er
    # return the files data
    return data


def saveJson(data, filepath, **kws):
    """
    This procedure saves given data to a json file

    :param kws: Json Dumps arguments , see standard python docs
    """

    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, **kws)
    except IOError:
        logger.error("Data not saved to file {}".format(filepath))
        return False

    logger.info("------->> file correctly saved to : {0}".format(filepath))

    return True


@contextlib.contextmanager
def loadFile(filepath):
    if filepath.endswith(".zip"):
        with zipfile.ZipFile(filepath, 'r') as f:
            yield f
        return
    elif ".zip" in filepath:
        # load from zipfile
        zippath, relativefilePath = filepath.split(".zip")
        zipPath = zippath + ".zip"

        with zipfile.ZipFile(zipPath, 'r') as zip:
            path = relativefilePath.replace("\\", "/").lstrip("/")
            for i in iter(zip.namelist()):
                if path == i:
                    yield zip.open(i)
                    break

        return
    with open(filepath) as f:
        yield f


def createZipWithProgress(zippath, files):
    """Same as function createZip() but has a stdout progress bar which is useful for commandline work
    :param zippath: the file path for the zip file
    :type zippath: str
    :param files: A Sequence of file paths that will be archived.
    :type files: seq(str)
    """
    dir = os.path.dirname(zippath)
    if not os.path.exists(os.path.join(dir, os.path.dirname(zippath))):
        os.makedirs(os.path.join(dir, os.path.dirname(zippath)))
    logger.debug("writing file: {}".format(zippath))
    length = len(files)
    progressBar = commandline.CommandProgressBar(length, prefix='Progress:', suffix='Complete', barLength=50)
    progressBar.start()
    with zipfile.ZipFile(zippath, "w", zipfile.ZIP_DEFLATED) as archive:
        for p in iter(files):
            logger.debug("Archiving file: {} ----> :{}\n".format(p[0], p[1]))
            archive.write(p[0], p[1])
            progressBar.increment(1)
    logger.debug("finished writing zip file to : {}".format(zippath))


def createZip(zippath, files):
    """Creates a zip file for the files, each path will be stored relative to the zippath which avoids abspath
    :param zippath: the file path for the zip file
    :type zippath: str
    :param files: A Sequence of file paths that will be archived.
    :type files: seq(str)
    """
    dir = os.path.dirname(zippath)
    if not os.path.exists(os.path.join(dir, os.path.dirname(zippath))):
        os.makedirs(os.path.join(dir, os.path.dirname(zippath)))
    logger.debug("writing file: {}".format(zippath))
    with zipfile.ZipFile(zippath, "w", zipfile.ZIP_DEFLATED) as archive:
        for p in iter(files):
            archive.write(p[0], p[1])
    logger.debug("finished writing zip file to : {}".format(zippath))