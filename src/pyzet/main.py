from __future__ import annotations

import argparse
from argparse import ArgumentParser
from argparse import Namespace

import pyzet.constants as C
from pyzet import show
from pyzet import utils
from pyzet.config import get
from pyzet.grep import define_grep_cli
from pyzet.grep import grep
from pyzet.ops import add_zettel
from pyzet.ops import clean_zet_repo
from pyzet.ops import count_tags
from pyzet.ops import edit_zettel
from pyzet.ops import get_remote_url
from pyzet.ops import init_repo
from pyzet.ops import list_tags
from pyzet.ops import list_zettels
from pyzet.ops import remove_zettel
from pyzet.sample_config import define_sample_config_cli
from pyzet.sample_config import sample_config
from pyzet.utils import add_pattern_args
from pyzet.utils import call_git


def main(argv: list[str] | None = None) -> int:
    utils.configure_console_print_utf8()

    parser, subparsers = _get_parser()
    args = parser.parse_args(argv)
    utils.setup_logger(utils.compute_log_level(args.verbose))

    if args.command == 'show' and args.show_cmd is None:
        subparsers['show'].print_usage()
        return 0
    if args.command is None:
        parser.print_usage()
        return 0
    try:
        return _parse_args(args)
    except BrokenPipeError:
        raise SystemExit


def _get_parser() -> tuple[ArgumentParser, dict[str, ArgumentParser]]:
    parser = argparse.ArgumentParser(
        prog='pyzet', formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers_dict = {}

    parser.add_argument('-r', '--repo', help='point to a custom ZK repo')
    parser.add_argument(
        '-c',
        '--config',
        default=C.DEFAULT_CFG_LOCATION,
        help='which config file to use (default: %(default)s)',
    )
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=f'%(prog)s {C.VERSION}',
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
        default=C.DEFAULT_BRANCH,
        help='initial branch name (default: %(default)s)',
    )

    subparsers.add_parser('add', help='add a new zettel')

    edit_parser = subparsers.add_parser('edit', help='edit an existing zettel')
    add_pattern_args(edit_parser)

    remove_parser = subparsers.add_parser('rm', help='remove a zettel')
    add_pattern_args(remove_parser)

    subparsers_dict['show'] = show.get_parser(subparsers)

    print_parser = subparsers.add_parser(
        'print',
        help="print zettel contents, shorthand for 'pyzet show text'",
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
    tags_parser.add_argument(
        '--count',
        action='store_true',
        help='count the total number of all tags in ZK repo (non-unique)',
    )

    clean_parser = subparsers.add_parser(
        'clean', help=f"delete empty folders in '{C.ZETDIR}' folder in ZK repo"
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
        default=C.DEFAULT_REMOTE_NAME,
        help='name of git repo remote (default: %(default)s)',
    )

    define_sample_config_cli(subparsers)

    return parser, subparsers_dict


def _add_git_cmd_options(parser: ArgumentParser, cmd_name: str) -> None:
    parser.add_argument(
        'options',
        action='store',
        type=str,
        nargs='*',
        default=[],
        help=f"pass 'git {cmd_name}' options, use '--' before including flags",
    )


def _parse_args(args: Namespace) -> int:
    if args.command == 'sample-config':
        return sample_config(args.kind)

    config = get(args)

    if args.command == 'show':
        return show.command(args, config)

    if args.command == 'print':
        args.show_cmd = 'text'
        return show.command(args, config)

    if args.command == 'rm':
        return remove_zettel(args, config)

    if args.command == 'init':
        return init_repo(config, args.initial_branch)

    if args.command == 'add':
        return add_zettel(config)

    if args.command == 'edit':
        return edit_zettel(args, config)

    if args.command == 'list':
        return list_zettels(args, config.repo)

    if args.command == 'tags':
        if args.count:
            return count_tags(config.repo)
        return list_tags(config.repo, is_reversed=args.reverse)

    if args.command == 'grep':
        return grep(args, config)

    if args.command in {'status', 'push'}:
        return call_git(config, args.command, args.options)

    if args.command == 'remote':
        return get_remote_url(args, config)

    if args.command == 'pull':
        # --rebase is used to maintain a linear history without merges,
        # as this seems to be a reasonable approach in ZK repo that is
        # usually personal.
        return call_git(config, 'pull', ('--rebase',))

    if args.command == 'clean':
        return clean_zet_repo(
            config.repo, is_dry_run=args.dry_run, is_force=args.force
        )
    raise NotImplementedError
