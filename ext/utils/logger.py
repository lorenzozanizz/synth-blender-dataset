"""Logging module for Random Dataset Generator addon."""

import logging
import sys
import time

from datetime import datetime
from pathlib import Path
from typing import Any, Union
from contextlib import contextmanager

class ExecutionContext:
    """Track metrics and timing for operations."""

    def __init__(self):
        self.metrics = {}
        self.errors = []

    def add_metric(self, key: str, value: Any):
        self.metrics[key] = value

    def add_error(self, op_name: str, error: str):
        self.errors.append({
            'operation': op_name,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })

class UniqueLogger:
    """

    """

    # A cache of the available logs for the files, each file requests
    # its own __name__ logger.
    _logger_cache = dict()
    _file_handler = None
    _output_path = None
    _console_handler = None
    _execution_ctx = ExecutionContext()

    # True if there is a valid log file, meaning that log can indeed happen.
    _initialized: bool = False

    @staticmethod
    def initialize_logging(log_dir: str, file_level=logging.DEBUG, console_level=logging.INFO) -> Union[str, Path]:
        """Initialize logging system once."""

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
        return UniqueLogger._initialized

    @staticmethod
    def get_path() -> Union[str, Path]:
        return UniqueLogger._output_path

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get or create logger for a module."""

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
    def get_execution_context() -> ExecutionContext:
        return UniqueLogger._execution_ctx

    @staticmethod
    @contextmanager
    def log_operation(name: str, category: str = None, logger: logging.Logger = None):
        """Context manager for operation tracking with timing."""

        logger = logger or logging.getLogger(__name__)
        start = time.time()

        logger.info(f"[{category}] Starting: {name}")
        try:
            yield
        except Exception as e:
            logger.error(f"Failed: {name} - {e}", exc_info=True)
            UniqueLogger._execution_ctx.add_error(name, str(e))
            raise
        finally:
            duration = time.time() - start
            logger.info(f"Completed: {name} ({duration:.2f}s)")

    @staticmethod
    def quick_log(text: str):
        logger = UniqueLogger.get_logger("default")
        logger.info(text)

    @staticmethod
    def cleanup():
        """Clean up logging on addon unload."""

        UniqueLogger._initialized = False

        for logger in UniqueLogger._logger_cache.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

        if UniqueLogger._file_handler:
            UniqueLogger._file_handler.close()
        if UniqueLogger._console_handler:
            UniqueLogger._console_handler.close()

        UniqueLogger._logger_cache.clear()