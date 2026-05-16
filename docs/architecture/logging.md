# Logging

## Overview

Rendersynth includes a lightweight logging system built on Python's standard `logging` module. The implementation lives in `ext/utils/logger.py` and is exposed as a single class, `UniqueLogger`, which acts as a centralized, stateful facade over the underlying loggers.

The system is opt-in: logging is disabled by default and only activates when the user provides a directory path in the Settings panel and clicks **Save path**. This triggers `ApplyLogPathOperator`, which calls `UniqueLogger.initialize_logging(directory)` and creates a timestamped log file at the given location.

---

## UniqueLogger

`UniqueLogger` is a static class rather than an instance. There is one shared file handler and one console handler across all modules. Individual modules request a named child logger via `UniqueLogger.get_logger(__name__)`, which is cached so the handlers are only attached once per name.

The log format for file output is:

```
2026-05-13 14:32:11,042 - [ext.pipeline.operations:INFO] - Compiled in 0.03s
```

The console format is more compact:

```
INFO     | ext.pipeline.operations    | Compiled in 0.03s
```

Before initialization, calls to `UniqueLogger.quick_log(text)` return immediately without raising. This means modules can log freely without defensive checks at each call site, they simply get no output until the user activates logging.

---

## Intended use with stochastic processes

The primary motivation for this system, as stated in the module docstring, is to record the outputs of the stochastic processes running during generation. When a batch of hundreds or thousands of images is produced, it is not always obvious after the fact what values were sampled from a distribution, which objects were hidden by a visibility pipe, or what positions were selected by a move operation. The log file provides a record that can be consulted for debugging, reproducibility analysis, or dataset auditing.

Each pipeline operation has access to `UniqueLogger` and can log the sampled values it acted on. As new pipes are added, logging calls should be placed at the point where a distribution is sampled and where the result is applied to a scene property. The `log_operation` context manager is available for timing blocks where the start, end, and elapsed time are worth recording:

```python
with UniqueLogger.log_operation("texture randomization", category="pipeline"):
    # the sampling and node assignment happen here
    ...
```

---

## Lifecycle

The logger is initialized manually by the user through the Settings panel and cleaned up automatically when the extension is unregistered (via the `unregister()` hook in `__init__.py`, which calls `UniqueLogger.cleanup()`). Cleanup closes all file handles, removes handlers from every cached logger, and resets the initialized state so a fresh call to `initialize_logging` works correctly in the same session.

Log files are named with a timestamp at creation time (`synth_logs_YYYY-MM-DD_HH-MM-SS.txt`), so successive sessions in the same directory do not overwrite each other.
