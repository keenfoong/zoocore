import datetime
import logging
import os

import jsonlogger
from zoo.libs.utils import classtypes

CENTRAL_LOGGER_NAME = "zoocore"


class ZooJsonFormatter(jsonlogger.JsonFormatter):
    """Overrriding the addFields since the timestamp is using utcnow instead of the local timezone.
    We also add support for static fields passed into the __init__
    """

    def __init__(self,
                 fmt="%(message)",
                 datefmt="%Y-%m-%dT%H:%M:%SZ%z",
                 style='%',
                 extra={}, *args, **kwargs):
        """
        :note: see :class:`jsonlogger.JsonFormatter` for information on arguments

        :param extra: static fields to pass to all records
        :type extra: dict
        """
        self._extra = extra
        jsonlogger.JsonFormatter.__init__(self, fmt=fmt, datefmt=datefmt, *args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        for field in self._required_fields:
            log_record[field] = record.__dict__.get(field)
        log_record.update(message_dict)
        jsonlogger.merge_record_extra(record, log_record, reserved=self._skip_fields)

        if self.timestamp:
            key = self.timestamp if type(self.timestamp) == str else 'timestamp'
            log_record[key] = datetime.datetime.now().isoformat()
        # add all the static extra fields into the record
        for key, value in self._extra.items():
            log_record[key] = value


class CentralLogManager(object):
    """This class is a singleton object that globally handles logging, any log added will managed by the class.
    """
    __metaclass__ = classtypes.Singleton

    def __init__(self):
        self.logs = {}
        self.jsonFormatter = "%(asctime) %(name) %(processName) %(pathname)  %(funcName) %(levelname) %(lineno) %(" \
                             "module) %(threadName) %(message)"
        self.rotateFormatter = "%(asctime)s: [%(process)d - %(name)s - %(levelname)s]: %(message)s"
        self.shellFormatter = "[%(name)s - %(levelname)s]: %(message)s"
        self.guiFormatter = "[%(name)s]: %(message)s"

    def addLog(self, logger):
        """Adds logger to this manager instance

        :param logger: the python logger instance.
        :type logger: :class:`logging.Logger`
        """
        if logger.name not in self.logs:
            self.logs[logger.name] = logger

    def removeLog(self, loggerName):
        """Remove's the logger instance by name

        :param loggerName: The logger instance name.
        :type: loggerName: str
        """
        if loggerName in self.logs:
            del self.logs[loggerName]

    def changeLevel(self, loggerName, level):
        """Changes the logger instance level.

        :param loggerName: The logger instance name.
        :type loggerName: str
        :param level: eg. logging.DEBUG.
        :type level: int
        """
        if loggerName in self.logs:
            log = self.logs[loggerName]
            if log.level != level:
                log.setLevel(level)

    def addRotateHandler(self, loggerName, filePath):
        logger = self.logs.get(loggerName)
        if not logger:
            return

        handler = logging.handlers.RotatingFileHandler(filePath, maxBytes=1.5e6, backupCount=5)
        handler.setFormatter(logging.Formatter(self.rotateFormatter))
        logger.addHandler(handler)
        return logger

    def addShellHandler(self, loggerName):
        logger = self.logs.get(loggerName)
        if not loggerName:
            return
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(self.shellFormatter))
        logger.addHandler(handler)
        return logger

    def addNullHandler(self, loggerName):
        logger = self.logs.get(loggerName)
        if not loggerName:
            return
        # Create an null handler
        io_handler = logging.NullHandler()
        # Create a logging formatter
        formatter = logging.Formatter(self.shellFormatter)
        # Assign the formatter to the io_handler
        io_handler.setFormatter(formatter)
        # Add the io_handler to the logger
        logger.addHandler(io_handler)
        io_handler.setLevel(logging.INFO)
        return logger


def logLevels():
    return [logging.getLevelName(n) for n in xrange(0, logging.CRITICAL + 1, 10)]


def levelsDict():
    return dict(zip(logLevels(), range(0, logging.CRITICAL + 1, 10)))


def getLogger(name):
    logger = logging.getLogger(name)
    globalLogLevelOverride(logger)
    CentralLogManager().addLog(logger)
    return logger


def globalLogLevelOverride(logger):
    globalLoggingLevel = os.environ.get("ZOO_LOG_LEVEL", "INFO")
    envLvl = levelsDict()[globalLoggingLevel]
    currentLevel = logger.getEffectiveLevel()

    if not currentLevel or currentLevel != envLvl:
        logger.setLevel(envLvl)


def reloadLoggerHierarchy():
    for log in logging.Logger.manager.loggingDict.values():
        if hasattr(log, "children"):
            del log.children
    for name, log in logging.Logger.manager.loggingDict.items():
        if not isinstance(log, logging.Logger):
            continue
        try:
            if log not in log.parent.children:
                log.parent.children.append(log)
        except AttributeError:
            log.parent.children = [log]


zooLogger = getLogger(CENTRAL_LOGGER_NAME)
# to avoid log messages propagating upwards in the
# log hierarchy.
zooLogger.propagate = False
handlers = zooLogger.handlers
if not handlers:
    CentralLogManager().addNullHandler(CENTRAL_LOGGER_NAME)
