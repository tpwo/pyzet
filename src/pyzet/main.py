from __future__ import annotations

import pyzet.cli
from pyzet import config
from pyzet import show
from pyzet import utils
from pyzet.cli import AppState
from pyzet.cli import get_parser
from pyzet.exceptions import NotFoundError
from pyzet.grep import grep
from pyzet.ops import add_zettel
from pyzet.ops import clean_zet_repo
from pyzet.ops import decide_whats_next
from pyzet.ops import edit_zettel
from pyzet.ops import get_remote_url
from pyzet.ops import info
from pyzet.ops import init_repo
from pyzet.ops import list_tags
from pyzet.ops import list_zettels
from pyzet.ops import remove_zettel
from pyzet.sample_config import sample_config
from pyzet.utils import call_git


def main(argv: list[str] | None = None) -> int:
    utils.configure_console_print_utf8()

    parser, subparsers = get_parser()
    args_cli = parser.parse_args(argv)
    utils.setup_logger(utils.compute_log_level(args_cli.verbose))
    args = pyzet.cli.populate_args(args_cli, parser)

    if args.command == 'show' and args.show_cmd is None:
        subparsers['show'].print_usage()
        return 0
    if args.command is None:
        parser.print_usage()
        return 0
    try:
        return _parse_args(args)
    except NotFoundError as err:
        raise SystemExit('aborting') from err
    except BrokenPipeError as err:
        raise SystemExit from err


def _parse_args(args: AppState) -> int:
    if args.command == 'sample-config':
        sample_config(args.kind)
        return 0

    looped_cmds = {'add', 'edit', 'rm', 'show', 'print', 'query'}
    cfg = config.get(args)

    if args.command in looped_cmds:
        if args.command == 'add':
            add_zettel(args, cfg)

        elif args.command == 'edit':
            edit_zettel(args, cfg)

        elif args.command == 'rm':
            remove_zettel(args, cfg)

        if args.command == 'show':
            show.command(args, cfg)

        elif args.command == 'print':
            args.show_cmd = 'text'
            show.command(args, cfg)

        if args.command == 'query':
            # Directly go to decide_whats_next
            print('Hello there! ', end='')

        decide_whats_next(args, cfg)

    else:
        if args.command == 'init':
            init_repo(cfg, args.initial_branch)

        elif args.command == 'list':
            list_zettels(args, cfg.repo)

        elif args.command == 'tags':
            list_tags(cfg.repo, is_reversed=args.reverse)

        elif args.command == 'grep':
            grep(args, cfg)

        elif args.command in {'status', 'push'}:
            call_git(cfg, args.command, args.options)

        elif args.command == 'remote':
            get_remote_url(args, cfg)

        elif args.command == 'pull':
            # --rebase is used to maintain a linear history without merges,
            # as this seems to be a reasonable approach in ZK repo that is
            # usually personal.
            call_git(cfg, 'pull', ('--rebase',))

        elif args.command == 'clean':
            clean_zet_repo(
                cfg.repo, is_dry_run=args.dry_run, is_force=args.force
            )

        elif args.command == 'info':
            info(cfg)

    return 0
