from __future__ import annotations

import pyzet.cli
from pyzet import config
from pyzet import ops
from pyzet import show
from pyzet import utils
from pyzet.cli import AppState
from pyzet.cli import get_parser
from pyzet.grep import grep
from pyzet.ops import add_zettel
from pyzet.ops import clean_zet_repo
from pyzet.ops import edit_zettel
from pyzet.ops import get_remote_url
from pyzet.ops import info
from pyzet.ops import init_repo
from pyzet.ops import list_tags
from pyzet.ops import list_zettels
from pyzet.ops import remove_zettel


def main(argv: list[str] | None = None) -> int:
    utils.configure_console_print_utf8()

    parser = get_parser()
    args_cli = parser.parse_args(argv)
    utils.setup_logger(utils.compute_log_level(args_cli.verbose))
    args = pyzet.cli.populate_args(args_cli, parser)

    if args.command is None:
        parser.print_usage()
        return 0
    try:
        return _parse_args(args)
    except BrokenPipeError as err:
        raise SystemExit from err


def _parse_args(args: AppState) -> int:
    if args.command == 'sample-config':
        print(utils.sample_config())
        return 0

    cfg = config.get(args)

    if args.command == 'query':
        return ops.query(args, cfg)
    elif args.command == 'add':
        return add_zettel(cfg)
    elif args.command == 'edit':
        return edit_zettel(args, cfg)
    elif args.command == 'rm':
        return remove_zettel(args, cfg)
    elif args.command == 'url':
        return show.url(args, cfg)
    elif args.command == 'mdlink':
        return show.mdlink(args, cfg)
    elif args.command == 'init':
        return init_repo(cfg, args.initial_branch)
    elif args.command == 'list':
        return list_zettels(args, cfg.repo)
    elif args.command == 'tags':
        return list_tags(cfg.repo, is_reversed=args.reverse)
    elif args.command == 'grep':
        return grep(args, cfg)
    elif args.command in {'status', 'push'}:
        return utils.call_git(cfg, args.command, args.options)
    elif args.command == 'remote':
        return get_remote_url(args, cfg)
    elif args.command == 'pull':
        # --rebase is used to maintain a linear history without merges,
        # as this seems to be a reasonable approach in ZK repo that is
        # usually personal.
        return utils.call_git(cfg, 'pull', ('--rebase',))
    elif args.command == 'clean':
        return clean_zet_repo(
            cfg.repo, is_dry_run=args.dry_run, is_force=args.force
        )
    elif args.command == 'info':
        return info(cfg)
    else:
        raise NotImplementedError
