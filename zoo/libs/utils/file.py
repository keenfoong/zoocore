import contextlib
import os
import json
import zipfile
import zlogging


from zoo.libs.utils import commandline

logger = zlogging.zooLogger


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
