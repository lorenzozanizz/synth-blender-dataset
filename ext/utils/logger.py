""" A module containing a logger used throughout the code. This logger is to be used
to analyze with fine-grained detail the outputs of the stochastic processes and the
choices taken by the constraints, when those will be implemented

Classes:
    UniqueLogger: The main logger class which can define multiple sub logs sources

Example:
    >>> from ext.utils.logger import UniqueLogger
    >>> ...
    >>> UniqueLogger.initialize_logging(...)
    >>> UniqueLogger.quick_log("This is a simple log")
"""

import logging
import sys
import time

from datetime import datetime
from pathlib import Path
from typing import Union
from contextlib import contextmanager

class UniqueLogger:
    """ A utility class to allow logging in the extension, internally uses the
    default python logger taking track of the time of operations. The generated
    Log file can be consulted when one wishes to see exactly the data sampled from
    the distributions or to check for errors.
    """

    # A cache of the available logs for the files, each file requests
    # its own __name__ logger.
    _logger_cache = dict()
    _file_handler = None
    _output_path = None
    _console_handler = None

    # True if there is a valid log file, meaning that log can indeed happen.
    _initialized: bool = False

    @staticmethod
    def initialize_logging(log_dir: str, file_level=logging.DEBUG, console_level=logging.INFO) -> Union[str, Path]:
        """ Initialize the unique logger for all modules, generating the output file at the given
        directory from the current time. This creates the file and console handler for the logger.

        From the moment this function is called, UniqueLogger.initialized() will return True

        :param log_dir: the directory for the new log file
        :param file_level: the logging level
        :param console_level: the console level
        :return: the path to the new log file
        """

        log_path = Path(log_dir)
        UniqueLogger._output_path = log_path
        log_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = log_path / f"synth_logs_{timestamp}.txt"

        # File handler
        UniqueLogger._file_handler = logging.FileHandler(str(log_file), encoding='utf-8')
        UniqueLogger._file_handler.setLevel(file_level)
        UniqueLogger._file_handler.setFormatter(
            logging.Formatter('%(asctime)s - [%(name)s:%(levelname)s] - %(message)s')
        )

        # Console handler
        UniqueLogger._console_handler = logging.StreamHandler(sys.stdout)
        UniqueLogger._console_handler.setLevel(console_level)
        UniqueLogger._console_handler.setFormatter(
            logging.Formatter('%(levelname)-8s | %(name)-20s | %(message)s')
        )

        UniqueLogger._initialized = True

        return log_path

    @staticmethod
    def available() -> bool:
        """ Returns whether there is a logger available e.g. initialize has been called before """
        return UniqueLogger._initialized

    @staticmethod
    def get_path() -> Union[str, Path]:
        """ Get the path at which the logger will be initialized and will write """
        return UniqueLogger._output_path

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """ Get the logger with the given name. If the logger has not
        been previously initialized, it will be created and stored into the cache.

        :param name:  name of the logger
        :return: the logging.Logger object
        """

        if name not in UniqueLogger._logger_cache:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            logger.propagate = False

            if UniqueLogger._file_handler:
                logger.addHandler(UniqueLogger._file_handler)
            if UniqueLogger._console_handler:
                logger.addHandler(UniqueLogger._console_handler)

            UniqueLogger._logger_cache[name] = logger

        return UniqueLogger._logger_cache[name]

    @staticmethod
    @contextmanager
    def log_operation(name: str, category: str = None, logger: logging.Logger = None):
        """ Context manager for operation tracking with timing. """

        logger = logger or logging.getLogger(__name__)
        start = time.time()

        logger.info(f"[{category}] Starting: {name}")
        try:
            yield
        except Exception as e:
            logger.error(f"Failed: {name} - {e}", exc_info=True)
            raise
        finally:
            duration = time.time() - start
            logger.info(f"Completed: {name} ({duration:.2f}s)")

    @staticmethod
    def quick_log(text: str) -> None:
        """ Logs text content to the log file using the default logger. Can only
        work properly if the logger has been previously initialized, otherwise
        it refuses silently to log.

        :param text: The text to be written to log file.
2        """
        if not UniqueLogger.available():
            return
        logger = UniqueLogger.get_logger("default")
        logger.info(text)

    @staticmethod
    def cleanup():
        """ Clean up logging on addon unload. """

        UniqueLogger._initialized = False

        # Remove ach previously registered handler, close every file handler and
        # any console handler.
        for logger in UniqueLogger._logger_cache.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

        if UniqueLogger._file_handler:
            UniqueLogger._file_handler.close()
        if UniqueLogger._console_handler:
            UniqueLogger._console_handler.close()

        UniqueLogger._logger_cache.clear()