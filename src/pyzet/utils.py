import io
import logging
import sys


def configure_console_print_utf8() -> None:
    # https://stackoverflow.com/a/60634040/14458327
    if isinstance(sys.stdout, io.TextIOWrapper):  # pragma: no cover
        # If statement is needed to satisfy mypy:
        # https://github.com/python/typeshed/issues/3049
        sys.stdout.reconfigure(encoding="utf-8")


def setup_logger(level: int) -> None:
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def compute_log_level(verbosity: int) -> int:
    """Matches chosen verbosity with default log levels from the logging module.

    Each verbosity increase (i.e. adding `-v` flag) should decrease a logging level by
    some value which is below called as 'verbosity_step'. Moreover, start log level, and
    minimum log level are defined.

    Logging module defines several log levels:

    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    """
    default_log_level = 30  # match WARNING level
    min_log_level = 10  # match DEBUG level
    verbosity_step = 10
    return max(default_log_level - verbosity_step * verbosity, min_log_level)
