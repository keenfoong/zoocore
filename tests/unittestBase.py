import inspect
import os
import tempfile
import unittest
import imp
from zoo.libs.utils import zlogging

logger = zlogging.getLogger(__name__)

class BaseUnitest(unittest.TestCase):
    """This Class acts as the base for all unitests, supplies a helper method for creating tempfile which
    will be cleaned up once the class has been shutdown.
    If you override the tearDownClass method you must call super or at least clean up the _createFiles set
    """
    _createdFiles = set()

    @classmethod
    def createTemp(cls, suffix):

        temp = tempfile.mkstemp(suffix=suffix)
        cls._createdFiles.add(temp)
        return temp

    @classmethod
    def addTempFile(cls, filepath):
        cls._createdFiles.add(filepath)

    @classmethod
    def tearDownClass(cls):
        super(BaseUnitest, cls).tearDownClass()
        for i in cls._createdFiles:
            if os.path.exists(i):
                os.remove(i)
        cls._createdFiles.clear()



def runTests(testSuite):
    if testSuite is None:
        return
    runner = unittest.TextTestRunner(verbosity=2, buffer=False, failfast=False)
    runner.run(testSuite)


if __name__ == '__main__':
    import logging

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    logger.setLevel(logging.DEBUG)
    testss = getTests("standalone").get("standalone")
    runTests(testss)
