from __future__ import annotations

import pyzet.constants as C
from pyzet import zettel
from pyzet.cli import AppState
from pyzet.config import Config
from pyzet.utils import get_git_remote_url
from pyzet.zettel import get_md_link
from pyzet.zettel import Zettel


def command(args: AppState, config: Config) -> None:
    if args.id is not None:
        zet = zettel.get_from_id(args.id, config.repo)
    elif args.patterns:
        zet = zettel.select_from_grep(args, config)
    else:
        zet = zettel.get_last(config.repo)

    args.id = zet.id

    if args.show_cmd == 'text':
        show_zettel(zet)
    elif args.show_cmd == 'mdlink':
        print(get_md_link(zet))

    elif args.show_cmd == 'url':
        remote = _remote_dot_git(get_git_remote_url(config, args.name))
        print(_get_zettel_url(remote, args.branch, zet.id))
    else:
        raise NotImplementedError


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
