from __future__ import annotations

import functools
import io
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class Config(NamedTuple):
    repo: Path
    editor: str


def call_git(
    config: Config,
    command: str,
    options: tuple[str, ...] | None = None,
    path: Path | None = None,
) -> int:
    if options is None:
        options = tuple()
    if path is None:
        path = config.repo
    cmd = [_get_git_bin(), '-C', path.as_posix(), command, *options]
    logging.debug(f'call_git: subprocess.run({cmd})')
    subprocess.run(cmd)
    return 0


def get_git_output(
    config: Config, command: str, options: tuple[str, ...]
) -> bytes:
    repo = config.repo.as_posix()
    cmd = [_get_git_bin(), '-C', repo, command, *options]
    logging.debug(f'get_git_output: subprocess.run({cmd})')
    return subprocess.run(cmd, capture_output=True, check=True).stdout


@functools.lru_cache(maxsize=1)
def _get_git_bin() -> str:
    if (git := shutil.which('git')) is None:
        raise SystemExit(f"ERROR: '{git}' cannot be found.")
    logging.debug(f"_get_git_bin: found at '{git}'")
    return git


def configure_console_print_utf8() -> None:
    # https://stackoverflow.com/a/60634040/14458327
    if isinstance(sys.stdout, io.TextIOWrapper):  # pragma: no cover
        # If statement is needed to satisfy mypy:
        # https://github.com/python/typeshed/issues/3049
        sys.stdout.reconfigure(encoding='utf-8')


def setup_logger(level: int) -> None:
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
    )


def compute_log_level(verbosity: int) -> int:
    """Matches chosen verbosity with default log levels from logging module.

    Each verbosity increase (i.e. adding `-v` flag) should decrease a
    logging level by some value which is below called as
    'verbosity_step'. Moreover, start log level, and minimum log level
    are defined.

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
