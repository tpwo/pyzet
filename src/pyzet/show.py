from __future__ import annotations

from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from pathlib import Path

import pyzet.constants as C
from pyzet.utils import Config
from pyzet.utils import get_git_remote_url
from pyzet.utils import get_md_relative_link
from pyzet.zettel import get_zettel


def get_parser(
    subparsers: _SubParsersAction[ArgumentParser],
) -> ArgumentParser:
    show_parser = subparsers.add_parser('show', help='print zettel contents')
    show_subparsers = show_parser.add_subparsers(dest='show_cmd')

    text_parser = show_subparsers.add_parser(
        'text', help='show zettel as plain text'
    )
    text_parser.add_argument(
        'id',
        nargs='?',
        help='zettel id, defaults to zettel with the newest timestamp',
    )

    link_parser = show_subparsers.add_parser(
        'mdlink', help='show zettel as a Markdown link'
    )
    link_parser.add_argument(
        'id',
        nargs='?',
        help='zettel id, defaults to zettel with the newest timestamp',
    )

    url_parser = show_subparsers.add_parser(
        'url', help='show zettel as an URL'
    )
    url_parser.add_argument(
        'id',
        nargs='?',
        help='zettel id, defaults to zettel with the newest timestamp',
    )
    url_parser.add_argument(
        '--origin',
        default=C.DEFAULT_REMOTE_NAME,
        help='name of git repo remote (default: %(default)s)',
    )
    url_parser.add_argument(
        '-b',
        '--branch',
        default=C.DEFAULT_BRANCH,
        help='initial branch name (default: %(default)s)',
    )

    return show_parser


def command(args: Namespace, config: Config, id_: str) -> int:
    if args.show_cmd == 'text':
        return show_zettel(id_, config.repo)
    if args.show_cmd == 'mdlink':
        return show_zettel_as_md_link(id_, config.repo)
    if args.show_cmd == 'url':
        return show_zettel_as_url(id_, args, config)
    raise NotImplementedError


def show_zettel(id_: str, repo_path: Path) -> int:
    """Prints zettel text prepended with centered ID as a header."""
    print(f' {id_} '.center(C.ZETTEL_WIDTH, '='))
    zettel_path = Path(repo_path, C.ZETDIR, id_, C.ZETTEL_FILENAME)
    with open(zettel_path, encoding='utf-8') as file:
        print(file.read(), end='')
    return 0


def show_zettel_as_md_link(id_: str, repo_path: Path) -> int:
    zettel_path = Path(repo_path, C.ZETDIR, id_)
    zettel = get_zettel(zettel_path)
    print(get_md_relative_link(zettel.id_, zettel.title))
    return 0


def show_zettel_as_url(id_: str, args: Namespace, config: Config) -> int:
    remote = _remote_dot_git(get_git_remote_url(config, args.origin))
    print(_get_zettel_url(remote, args.branch, id_))
    return 0


def _remote_dot_git(remote: str) -> str:
    """Remove '.git' suffix from remote URL."""
    return remote.partition('.git')[0]


def _get_zettel_url(repo_url: str, branch: str, id_: str) -> str:
    """Returns zettel URL for the most popular Git online hostings."""
    if 'github.com' in repo_url:
        return f'{repo_url}/tree/{branch}/{C.ZETDIR}/{id_}'
    if 'gitlab.com' in repo_url:
        return f'{repo_url}/-/tree/{branch}/{C.ZETDIR}/{id_}'
    if 'bitbucket.org' in repo_url:
        return f'{repo_url}/src/{branch}/{C.ZETDIR}/{id_}'
    raise NotImplementedError
