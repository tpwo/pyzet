from __future__ import annotations

import functools
import io
import logging
import os
import pydoc
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

from pyzet.constants import DEFAULT_CFG_LOCATION

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from pyzet.config import Config


def call_git(
    config: Config,
    command: str,
    options: Iterable[str] = (),
    path: Path | None = None,
) -> int:
    """Call git with a given command and return subprocess return code."""
    if path is None:
        path = config.repo
    cmd = (_get_git_bin(), '-C', path.as_posix(), command, *options)
    logging.debug('call_git: subprocess.run(%s)', cmd)
    res = subprocess.run(cmd)

    return res.returncode


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


def sample_config() -> str:
    return f"""\
# See https://github.com/tpwo/pyzet for more information.
#
# Put this file at {DEFAULT_CFG_LOCATION}
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: {get_default_editor()}
editor_args: []\
"""


def get_default_editor() -> str:
    """Get default editor PATH.

    On Windows it's the default path to Vim bundled with Git for Windows.

    On different systems (i.e. Unix) we refer to `EDITOR`, and then `VISUAL` env vars.
    """
    if editor := os.getenv('EDITOR'):
        return editor
    else:
        if visual := os.getenv('VISUAL'):
            return visual
        else:
            raise SystemExit(
                'ERROR: cannot get the default editor\n'
                f'Define `EDITOR` or `VISUAL` env var or configure `editor` in `{DEFAULT_CFG_LOCATION}`.'
            )


def page_output(text: str) -> None:
    """Display text in a pager only if output is longer than terminal height.

    Replicates the `-F` / `--quit-if-one-screen` option from less, i.e.
    automatically exits/prints directly if the entire file can be displayed on
    the first screen. Uses the system pager (less, more, etc.) if available and
    output is longer than terminal height. Otherwise, prints directly to
    stdout.
    """
    lines = text.splitlines()

    # NOTE: This can fail if not running in interactive terminal (e.g. CI), but
    # now it's not called in this use cases.
    _, terminal_height = shutil.get_terminal_size()

    # Terminal height minus one for command prompt and one for safety margin
    available_height = max(terminal_height - 2, 1)

    if len(lines) <= available_height:
        # Output fits on screen, print directly without paging
        print(text)
    else:
        # This is not documented, but works out of the box without running any
        # subprocesses and looking at env variables. Reference:
        # https://stackoverflow.com/a/18234081/14458327
        pydoc.pager(text)
