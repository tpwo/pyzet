from __future__ import annotations

import argparse
import logging
from argparse import ArgumentParser
from argparse import Namespace
from argparse import _SubParsersAction
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import TYPE_CHECKING
from typing import TypeVar

import pyzet.constants as const

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


@dataclass
class AppState:
    """Represents the current state of the app."""

    command: str
    config: str
    id: str | None
    patterns: list[str]
    tags: bool
    link: bool
    pretty: bool
    line_number: bool
    force: bool
    dry_run: bool
    options: Iterable[str]
    initial_branch: str
    reverse: bool
    title: bool
    repo: str
    path: Path
    name: str
    branch: str
    verbose: int
    kind: str


T = TypeVar('T')


def populate_args(args_cli: Namespace, parser: ArgumentParser) -> AppState:
    """Populate AppState with values from CLI and parser defaults."""

    def get_initial(name: str) -> T:  # type: ignore[type-var]
        """Get initial value from CLI or from parser defaults."""
        try:
            return args_cli.__getattribute__(name)
        except AttributeError:
            return parser.get_default(name)

    state = AppState(
        command=get_initial('command'),
        config=get_initial('config'),
        id=get_initial('id'),
        patterns=get_initial('patterns'),
        tags=get_initial('tags'),
        link=get_initial('link'),
        pretty=get_initial('pretty'),
        line_number=get_initial('line_number'),
        force=get_initial('force'),
        dry_run=get_initial('dry_run'),
        options=get_initial('options'),
        initial_branch=get_initial('initial_branch'),
        reverse=get_initial('reverse'),
        title=get_initial('title'),
        repo=get_initial('repo'),
        path=get_initial('path'),
        name=get_initial('name'),
        branch=get_initial('branch'),
        verbose=get_initial('verbose'),
        kind=get_initial('kind'),
    )
    logging.info(f'populate_args: {state}')
    return state


def get_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='pyzet', formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-r', '--repo', help='point to a custom ZK repo')
    parser.add_argument(
        '-c',
        '--config',
        default=const.DEFAULT_CFG_LOCATION,
        help='which config file to use (default: %(default)s)',
    )
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=f'%(prog)s {const.VERSION}',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='increase verbosity of the output',
    )

    subparsers = parser.add_subparsers(dest='command')

    init_parser = subparsers.add_parser(
        'init', help='initialize a git ZK repo at configured or given path'
    )
    init_parser.add_argument(
        'path',
        nargs='?',
        help='use a different dir than specified in the config file;'
        ' if target dir exists, it must be empty',
    )
    init_parser.add_argument(
        '-b',
        '--initial-branch',
        default=const.DEFAULT_BRANCH,
        help='initial branch name (default: %(default)s)',
    )

    subparsers.add_parser('add', help='add a new zettel')

    url_parser = subparsers.add_parser('url', help='get URL to a zettel')
    url_parser.add_argument(
        '--name',
        default=const.DEFAULT_REMOTE_NAME,
        help='name of git repo remote (default: %(default)s)',
    )
    url_parser.add_argument(
        '-b',
        '--branch',
        default=const.DEFAULT_BRANCH,
        help='initial branch name (default: %(default)s)',
    )
    add_pattern_args(url_parser)

    mdlink_parser = subparsers.add_parser(
        'mdlink', help='get Markdown link to a zettel'
    )
    add_pattern_args(mdlink_parser)

    edit_parser = subparsers.add_parser('edit', help='edit an existing zettel')
    add_pattern_args(edit_parser)

    remove_parser = subparsers.add_parser('rm', help='remove a zettel')
    add_pattern_args(remove_parser)

    print_parser = subparsers.add_parser(
        'print',
        help="print zettel contents, a shorthand for 'pyzet show text'",
    )
    add_pattern_args(print_parser)

    list_parser = subparsers.add_parser('list', help='list all zettels')
    list_parser.add_argument(
        '-p',
        '--pretty',
        action='store_true',
        help='use prettier format for printing date and time',
    )
    list_parser.add_argument(
        '--tags',
        action='store_true',
        help='show tags for each zettel',
    )
    list_parser.add_argument(
        '-l',
        '--link',
        action='store_true',
        help='print zettels as relative Markdown'
        ' links for pasting in other zettels',
    )
    list_parser.add_argument(
        '-r',
        '--reverse',
        action='store_true',
        help='reverse the output (newest first)',
    )

    tags_parser = subparsers.add_parser(
        'tags', help='list all tags and count them'
    )
    tags_parser.add_argument(
        '-r',
        '--reverse',
        action='store_true',
        help='reverse the output',
    )

    clean_parser = subparsers.add_parser(
        'clean',
        help=f"delete empty folders in '{const.ZETDIR}' folder in ZK repo",
    )
    clean_parser.add_argument(
        '-d',
        '--dry-run',
        action='store_true',
        help="list what will be deleted, but don't delete it",
    )
    clean_parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='force, use it to actually delete anything',
    )

    define_grep_cli(subparsers)

    status_parser = subparsers.add_parser(
        'status', help="run 'git status' in ZK repo"
    )
    _add_git_cmd_options(status_parser, 'status')

    subparsers.add_parser('pull', help="run 'git pull --rebase' in ZK repo")

    push_parser = subparsers.add_parser(
        'push', help="run 'git push' in ZK repo"
    )
    _add_git_cmd_options(push_parser, 'push')

    remote_parser = subparsers.add_parser(
        'remote', help="run 'git remote get-url' in ZK repo"
    )
    remote_parser.add_argument(
        '--name',
        default=const.DEFAULT_REMOTE_NAME,
        help='name of git repo remote (default: %(default)s)',
    )

    subparsers.add_parser('info', help='show stats about ZK repo')

    query_parser = subparsers.add_parser('query', help='query ZK repo')
    query_parser.add_argument(
        'patterns',
        nargs='+',
        help="grep patterns, pass 'git grep' options after '--'",
    )

    sample_config_parser = subparsers.add_parser(
        'sample-config', help=f'produce a sample {const.CONFIG_FILE} file'
    )
    sample_config_parser.add_argument('kind', choices=('unix', 'windows'))

    return parser


def define_grep_cli(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    grep_parser = subparsers.add_parser(
        'grep', help="run 'git grep' with some handy flags in ZK repo"
    )
    grep_parser.add_argument(
        '-t',
        '--title',
        action='store_true',
        help='add zettel title to matching lines',
    )
    grep_parser.add_argument(
        '-n',
        '--line-number',
        action='store_true',
        help='prefix the line number to matching lines',
    )
    grep_parser.add_argument(
        'patterns',
        nargs='+',
        help="grep patterns, pass 'git grep' options after '--'",
    )


def _add_git_cmd_options(parser: ArgumentParser, cmd_name: str) -> None:
    parser.add_argument(
        'options',
        action='store',
        type=str,
        nargs='*',
        default=[],
        help=f"pass 'git {cmd_name}' options, use '--' before including flags",
    )


def add_pattern_args(parser: ArgumentParser) -> None:
    parser.add_argument('patterns', nargs='*', help='grep patterns')
    parser.add_argument(
        '-p',
        '--pretty',
        action='store_true',
        help='use prettier format for printing date and time',
    )
    parser.add_argument(
        '--tags',
        action='store_true',
        help='show tags for each zettel',
    )
    parser.add_argument(
        '--id', type=valid_id, help='provide zettel ID instead of patterns'
    )


def valid_id(id_: str) -> str:
    """Gradually checks if given string is a valid zettel id."""
    try:
        int(id_)
    except ValueError as err:
        raise argparse.ArgumentTypeError(
            f"'{id_}' is not a valid zettel id (not an integer)"
        ) from err
    if len(id_) != const.ZULU_FORMAT_LEN:
        raise argparse.ArgumentTypeError(
            f"'{id_}' is not a valid zettel id ({_get_id_err_details(id_)})"
        )
    try:
        datetime.strptime(id_, const.ZULU_DATETIME_FORMAT).replace(
            tzinfo=timezone.utc
        )
    except ValueError as err:
        raise argparse.ArgumentTypeError(
            f"'{id_}' is not a valid zettel id"
        ) from err
    else:
        return id_


def _get_id_err_details(id_: str) -> str:
    """Generate error msg based on the diff in expected and actual chars."""
    num = len(id_) - const.ZULU_FORMAT_LEN
    s = 's' if num > 1 else ''
    diff = 'long' if num > 0 else 'short'
    return f'{num} char{s} too {diff}'
