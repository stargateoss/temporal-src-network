# pyright: reportOptionalMemberAccess=false, reportGeneralTypeIssues=false

import logging
import sys

class Logger():
    "Logger core class"

    LOG_LEVEL_OFF = -1
    """
    The log level to log nothing.
    """

    LOG_LEVEL_NORMAL = logging.INFO
    """
    The log level to log error, warn and info messages and stacktraces.
    """

    LOG_LEVEL_DEBUG = logging.DEBUG
    """
    The log level to log debug messages.
    """

    LOG_LEVEL_VERBOSE = logging.DEBUG - 1
    """
    The log level to log verbose messages.
    """

    LOG_LEVEL_VVERBOSE = logging.DEBUG - 2
    """
    The log level to log very verbose messages.
    """

    LOG_LEVELS = [LOG_LEVEL_OFF, LOG_LEVEL_NORMAL, LOG_LEVEL_DEBUG, LOG_LEVEL_VERBOSE, LOG_LEVEL_VVERBOSE]
    DEFAULT_LOG_LEVEL = LOG_LEVEL_NORMAL

    def __init__(self):
        self.logger_impl = None
        self.logger_log_formatter = None

    def setup_logger(self, logger_name=None, logger_log_level=None, logger_log_formatter=None):
        "Setup the logger with optionally the logger name, log level and format passed."

        if self.logger_impl:
            return

        logger_name = "root" if not logger_name else str(logger_name)

        add_logging_level("VERBOSE", Logger.LOG_LEVEL_VERBOSE)
        add_logging_level("VVERBOSE", Logger.LOG_LEVEL_VVERBOSE)

        self.logger_impl = logging.getLogger(logger_name)

        # Must be called before handlers as it reads logger_impl.level
        self.set_log_level(logger_log_level)

        self.set_log_handlers(logger_log_formatter)

    def get_log_level(self):
        return self.logger_impl.level

    def set_log_level(self, logger_log_level):
        logger_impl = self.logger_impl
        if not logger_impl or not isinstance(logger_impl, logging.Logger):
            return Logger.DEFAULT_LOG_LEVEL

        if logger_log_level is None or not isinstance(logger_log_level, int) or \
            logger_log_level not in Logger.LOG_LEVELS:
            logger_log_level = Logger.DEFAULT_LOG_LEVEL

        if logger_log_level == Logger.LOG_LEVEL_OFF:
            logger_impl.disabled = True
            logger_impl.setLevel(logging.CRITICAL)
        else:
            logger_impl.disabled = False
            logger_impl.setLevel(logger_log_level)

        return logger_log_level

    def set_log_handlers(self, logger_log_formatter):
        logger_impl = self.logger_impl

        if logger_log_formatter is None:
            logger_log_formatter = LoggerFormatter()

        logger_log_level = self.get_log_level()

        # Redirect all messages to stdout
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logger_log_level)
        # console_handler.setFormatter(logger_log_formatter)
        # logger.addHandler(console_handler)

        # Redirect INFO and DEEBUG messages to stdout
        console_handler_stdout = logging.StreamHandler(sys.stdout)
        console_handler_stdout.setLevel(logger_log_level)
        console_handler_stdout.addFilter(LoggerLessThanFilter(logging.WARNING))
        console_handler_stdout.setFormatter(logger_log_formatter)
        logger_impl.addHandler(console_handler_stdout)

        # Redirect WARNING and above messages to stderr
        console_handler_stderr = logging.StreamHandler(sys.stderr)
        console_handler_stderr.setLevel(logging.WARNING)
        console_handler_stderr.setFormatter(logger_log_formatter)
        logger_impl.addHandler(console_handler_stderr)

        self.logger_log_formatter = logger_log_formatter


    def get_logger_impl(self):
        return self.logger_impl

    def get_tag_prefix(self, tag):
        return "{:22s}".format(tag) # pylint: disable=consider-using-f-string

    def vverbose(self, tag, msg, *args, **kwargs):
        self.logger_impl.vverbose(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def verbose(self, tag, msg, *args, **kwargs):
        self.logger_impl.verbose(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def debug(self, tag, msg, *args, **kwargs):
        self.logger_impl.debug(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def info(self, tag, msg, *args, **kwargs):
        self.logger_impl.info(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def warn(self, tag, msg, *args, **kwargs):
        self.logger_impl.warning(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def error(self, tag, msg, *args, **kwargs):
        self.logger_impl.error(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def error_debug(self, tag, msg, *args, **kwargs):
        if self.get_log_level() <= Logger.LOG_LEVEL_DEBUG:
            self.logger_impl.error(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def error_verbose(self, tag, msg, *args, **kwargs):
        if self.get_log_level() <= Logger.LOG_LEVEL_VERBOSE:
            self.logger_impl.error(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def error_vverbose(self, tag, msg, *args, **kwargs):
        if self.get_log_level() <= Logger.LOG_LEVEL_VVERBOSE:
            self.logger_impl.error(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def critical(self, tag, msg, *args, **kwargs):
        self.logger_impl.critical(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def exception(self, tag, msg, *args, **kwargs):
        self.logger_impl.exception(self.get_tag_prefix(tag) + msg, *args, **kwargs)

    def log(self, priority, msg, *args, **kwargs):
        self.logger_impl.log(priority, msg, *args, **kwargs)

    def shutdown(self):
        self.logger_impl.shutdown()

    def log_debug_no_format(self, msg, *args, **kwargs):
        "Log the message at 'DEBUG' level directly without any format."

        self.logger_log_formatter.set_no_logger_format(True)
        self.logger_impl.debug(msg, *args, **kwargs)
        self.logger_log_formatter.set_no_logger_format(False)

    def log_verbose_no_format(self, msg, *args, **kwargs):
        "Log the message at 'VERBOSE' level directly without any format."

        self.logger_log_formatter.set_no_logger_format(True)
        self.logger_impl.verbose(msg, *args, **kwargs)
        self.logger_log_formatter.set_no_logger_format(False)

logger = Logger()

class LoggerFormatter(logging.Formatter):
    "Logger format class"

    root_logger_format = "[%(levelname).1s] %(message)s"
    # root_logger_format = "[%(levelname).1s] %(funcName)s: %(message)s"

    named_logger_format = "[%(levelname).1s] %(name)s: %(message)s"
    # named_logger_format = "[%(levelname).1s] %(name)s: %(funcName)s: %(message)s"

    def __init__(self):
        super().__init__()
        self.no_logger_format = False
        self.custom_logger_format = None

    def set_no_logger_format(self, state):
        self.no_logger_format = state
        self.custom_logger_format = None

    def set_custom_logger_format(self, custom_logger_format):
        self.no_logger_format = False
        self.custom_logger_format = custom_logger_format

    def format(self, record):
        # pylint: disable=protected-access

        if self.no_logger_format:
            self._style._fmt = "%(message)s"
        elif self.custom_logger_format:
            self._style._fmt = self.custom_logger_format
        elif record.name == "root":
            self._style._fmt = self.root_logger_format
        else:
            self._style._fmt = self.named_logger_format
        return super().format(record)


class LoggerLessThanFilter(logging.Filter):
    "Logger log level filtering class"

    def __init__(self, exclusive_maximum, name=""):
        super().__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # Non-zero return means the message will be logged
        return 1 if record.levelno < self.max_level else 0



def add_logging_level(level_name, level_num, method_name=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `level_name` becomes an attribute of the `logging` module with the value
    `level_num`. `method_name` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `method_name` is not specified, `level_name.lower()`
    is used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present.

    Example
    -------
    >>> add_logging_level('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    - https://stackoverflow.com/a/35804945
    """
    # pylint: disable=consider-using-f-string

    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError('{} already defined in logging module'.format(level_name))
    if hasattr(logging, method_name):
        raise AttributeError('{} already defined in logging module'.format(method_name))
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError('{} already defined in logger class'.format(method_name))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, logForLevel)
    setattr(logging, method_name, logToRoot)
