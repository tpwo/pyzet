from __future__ import annotations

from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace

import pyzet.constants as C
from pyzet import zettel
from pyzet.config import Config
from pyzet.ops import edit_zettel
from pyzet.utils import add_pattern_args
from pyzet.utils import get_git_remote_url
from pyzet.zettel import get_md_link
from pyzet.zettel import Zettel


def get_parser(
    subparsers: _SubParsersAction[ArgumentParser],
) -> ArgumentParser:
    show_parser = subparsers.add_parser(
        'show', help='show zettel in a chosen representation'
    )
    show_subparsers = show_parser.add_subparsers(dest='show_cmd')

    text_parser = show_subparsers.add_parser(
        'text', help='show zettel as plain text'
    )
    add_pattern_args(text_parser)

    link_parser = show_subparsers.add_parser(
        'mdlink', help='show zettel as a Markdown link'
    )
    add_pattern_args(link_parser)

    url_parser = show_subparsers.add_parser(
        'url', help='show zettel as an URL'
    )
    url_parser.add_argument(
        '--name',
        default=C.DEFAULT_REMOTE_NAME,
        help='name of git repo remote (default: %(default)s)',
    )
    url_parser.add_argument(
        '-b',
        '--branch',
        default=C.DEFAULT_BRANCH,
        help='initial branch name (default: %(default)s)',
    )
    add_pattern_args(url_parser)

    return show_parser


def command(args: Namespace, config: Config) -> int:
    if args.patterns:
        zet = zettel.get_from_grep(args, config)
    elif args.id is not None:
        zet = zettel.get_from_id(args.id, config.repo)
    else:
        zet = zettel.get_last(config.repo)

    if args.show_cmd == 'text':
        show_zettel(zet)

    if args.show_cmd == 'mdlink':
        print(get_md_link(zet))

    if args.show_cmd == 'url':
        remote = _remote_dot_git(get_git_remote_url(config, args.name))
        print(_get_zettel_url(remote, args.branch, zet.id))

    try:
        if input('Enter editor (y/N)? ') != 'y':
            raise SystemExit('aborting')
    except KeyboardInterrupt:
        raise SystemExit('\naborting')
    else:
        return edit_zettel(args, config)


def show_zettel(zet: Zettel) -> None:
    """Prints zettel text prepended with centered ID as a header."""
    fillchar = '='
    print(f' {zet.id} '.center(C.ZETTEL_WIDTH, fillchar))
    with open(zet.path, encoding='utf-8') as file:
        print(file.read(), end='')
    print(''.center(C.ZETTEL_WIDTH, fillchar))


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
