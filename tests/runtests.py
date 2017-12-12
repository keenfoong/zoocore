import subprocess
import argparse
import os
import errno
import stat
import logging

logger = logging.debug(__name__)


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
    cmd = ["python", os.path.join(os.path.dirname(os.path.realpath(__file__)), "unittestBase.py")]
    try:
        logger.debug("Booting with cmd :: {}".format(cmd))
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        logger.error("hard crashed during unittests", exc_info=True)


if __name__ == '__main__':
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    main()
