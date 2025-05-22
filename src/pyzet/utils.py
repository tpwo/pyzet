from __future__ import annotations

import functools
import io
import logging
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from pyzet.config import Config


def call_git(
    config: Config,
    command: str,
    options: Iterable[str] = (),
    path: Path | None = None,
) -> None:
    if path is None:
        path = config.repo
    cmd = (_get_git_bin(), '-C', path.as_posix(), command, *options)
    logging.debug('call_git: subprocess.run(%s)', cmd)
    subprocess.run(cmd)


def get_git_remote_url(
    config: Config,
    origin: str,
    options: Iterable[str] = (),
) -> str:
    opts = ('get-url', origin, *options)
    remote = get_git_output(config, 'remote', opts).decode().strip()

    if remote.startswith('git@'):  # This breaks if someone uses 'ssh://' URL
        return _convert_ssh_to_https(remote)
    else:
        return remote


def get_git_output(
    config: Config, command: str, options: Iterable[str]
) -> bytes:
    repo = config.repo.as_posix()
    cmd = (_get_git_bin(), '-C', repo, command, *options)
    logging.debug('get_git_output: subprocess.run(%s)', cmd)
    try:
        return subprocess.run(cmd, capture_output=True, check=True).stdout
    except subprocess.CalledProcessError as err:
        if command == 'grep':
            # Grep returns non-zero exit code if no match,
            # but without any error msg
            raise
        errmsg = err.stderr.decode().strip()
        raise SystemExit(f'GIT ERROR:\n{errmsg}') from err


def _convert_ssh_to_https(remote: str) -> str:
    """Convert Git SSH url into HTTPS url."""
    return 'https://' + remote.partition('git@')[-1].replace(':', '/')


@functools.lru_cache(maxsize=1)
def _get_git_bin() -> str:
    if (git := shutil.which('git')) is None:
        raise SystemExit(f"ERROR: '{git}' cannot be found.")
    logging.debug("_get_git_bin: found at '%s'", git)
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
    """Match chosen verbosity with default log levels from logging module.

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
