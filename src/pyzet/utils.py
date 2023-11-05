from __future__ import annotations

import argparse
import functools
import io
import logging
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import Iterable
from typing import NamedTuple

import pyzet.constants as C
from pyzet.zettel import Zettel


class Config(NamedTuple):
    repo: Path
    editor: str
    editor_args: tuple[str, ...]


def call_git(
    config: Config,
    command: str,
    options: Iterable[str] = (),
    path: Path | None = None,
) -> int:
    if path is None:
        path = config.repo
    cmd = (_get_git_bin(), '-C', path.as_posix(), command, *options)
    logging.debug(f'call_git: subprocess.run({cmd})')
    subprocess.run(cmd)
    return 0


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
    logging.debug(f'get_git_output: subprocess.run({cmd})')
    try:
        return subprocess.run(cmd, capture_output=True, check=True).stdout
    except subprocess.CalledProcessError as err:
        if command == 'grep':
            # Grep returns non-zero exit code if no match,
            # but without any error msg
            raise
        git_err_prefix = 'error: '
        errmsg = err.stderr.decode().strip().partition(git_err_prefix)[-1]
        raise SystemExit(f'GIT ERROR: {errmsg}') from err


def _convert_ssh_to_https(remote: str) -> str:
    """Converts Git SSH url into HTTPS url."""
    return 'https://' + remote.partition('git@')[-1].replace(':', '/')


def get_md_relative_link(zet: Zettel) -> str:
    """Returns a representation of a zettel that is a relative Markdown link.

    Asterisk at the beginning is a Markdown syntax for an unordered list,
    as links to zettels are usually just used in references section of a
    zettel.
    """
    return f'* [{zet.id}](../{zet.id}) {zet.title}'


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


def add_id_arg(parser: ArgumentParser) -> None:
    parser.add_argument(
        'id',
        nargs='?',
        type=valid_id,
        help='zettel id (default: newest zettel)',
    )


def valid_id(id_: str) -> str:
    try:
        datetime.strptime(id_, C.ZULU_DATETIME_FORMAT)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{id_}' is not a valid zettel id")
    else:
        return id_
