from __future__ import annotations

import argparse
import itertools
import logging
import shutil
import subprocess
from argparse import ArgumentParser
from argparse import Namespace
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

import yaml

import pyzet.constants as C
from pyzet import show
from pyzet import utils
from pyzet import zettel
from pyzet.grep import define_grep_cli
from pyzet.grep import grep
from pyzet.sample_config import define_sample_config_cli
from pyzet.sample_config import sample_config
from pyzet.utils import add_pattern_args
from pyzet.utils import call_git
from pyzet.utils import Config
from pyzet.utils import get_git_output
from pyzet.utils import get_git_remote_url


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
    return _parse_args(args)


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
        '--origin',
        default=C.DEFAULT_REMOTE_NAME,
        help='name of git repo remote (default: %(default)s)',
    )
    _add_git_cmd_options(remote_parser, 'remote')

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

    config = _get_config(args)

    if args.command == 'show':
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


def _get_config(args: Namespace) -> Config:
    """Gets config from YAML."""
    try:
        with open(args.config) as file:
            yaml_cfg = yaml.safe_load(file)
    except FileNotFoundError:
        raise SystemExit(
            f"ERROR: config file at '{Path(args.config).as_posix()}' "
            "not found.\nAdd it or use '--config' flag."
        )
    config = process_yaml(yaml_cfg, args.config, args.repo)
    # if we initialize repo, the folder may not exist
    if args.command == 'init':
        if args.path:
            return config._replace(repo=Path(args.path))
        return config
    if not config.repo.is_dir():
        raise SystemExit(
            'ERROR: wrong repo path. '
            "Run 'pyzet init' to create a git repo at "
            f"'{config.repo}', or use '--repo' flag."
        )
    return config


def process_yaml(
    yaml_cfg: dict[str, object], config_file: str, repo_path: str | None = None
) -> Config:
    """Processes YAML config file.

    Only 'repo' field is required. If other fields are missing,
    a default value will be used.
    """
    if repo_path:
        repo = Path(repo_path)
    else:
        try:
            repo_raw = yaml_cfg['repo']
            assert isinstance(repo_raw, str)
            repo = Path(repo_raw).expanduser()
        except KeyError:
            raise SystemExit(
                "ERROR: field 'repo' missing from"
                f" '{Path(config_file).as_posix()}'."
            )

    editor = yaml_cfg.get('editor', C.VIM_PATH)
    assert isinstance(editor, str)

    editor_args = yaml_cfg.get('editor_args', [])
    assert isinstance(editor_args, Iterable)

    return Config(
        repo=repo,
        editor=editor,
        editor_args=tuple(editor_args),
    )


def get_remote_url(args: Namespace, config: Config) -> int:
    print(get_git_remote_url(config, args.origin, args.options))
    return 0


def list_zettels(args: Namespace, path: Path) -> int:
    for zet in zettel.get_all(Path(path, C.ZETDIR), args.reverse):
        print(zettel.get_repr(zet, args))
    return 0


def list_tags(path: Path, is_reversed: bool) -> int:
    zettels = zettel.get_all(Path(path, C.ZETDIR))
    all_tags = itertools.chain.from_iterable(
        t for t in (z.tags for z in zettels)
    )
    # Chain is reverse sorted for the correct alphabetical displaying of
    # tag counts. This is because Counter's most_common() method
    # remembers the insertion order.
    tags = Counter(sorted(all_tags, reverse=True))

    target = (
        tags.most_common() if is_reversed else reversed(tags.most_common())
    )
    print(*(f'{occurrences}\t#{tag}' for tag, occurrences in target), sep='\n')
    return 0


def count_tags(path: Path) -> int:
    dir = Path(path, C.ZETDIR)
    print(sum(len(zettel.tags) for zettel in zettel.get_all(dir)))
    return 0


def clean_zet_repo(repo_path: Path, is_dry_run: bool, is_force: bool) -> int:
    is_any_empty = False
    for folder in sorted(Path(repo_path, C.ZETDIR).iterdir(), reverse=True):
        if folder.is_dir() and _is_empty(folder):
            is_any_empty = True
            if is_force and not is_dry_run:
                print(f'deleting {folder.name}')
                folder.rmdir()
            else:
                print(f'will delete {folder.name}')
    if is_any_empty and not is_force:
        print("use '--force' to proceed with deletion")
    return 0


def init_repo(config: Config, branch_name: str) -> int:
    """Initializes a git repository in a given path."""
    # We create both main ZK folder, and the folder that keeps all the
    # zettels. This is split, as each one can raise an Exception, and
    # we'd like to have a nice error message in such case.
    _create_empty_folder(config.repo)
    _create_empty_folder(Path(config.repo, C.ZETDIR))
    call_git(config, 'init', ('--initial-branch', branch_name))
    logging.info(f"init: create git repo '{config.repo.absolute()}'")
    return 0


def _create_empty_folder(path: Path) -> None:
    """Creates empty folder or does nothing if it exists."""
    if path.exists():
        if not path.is_dir():
            raise SystemExit(
                f"ERROR: '{path.as_posix()}' exists and is a file."
            )
        if not _is_empty(path):
            raise SystemExit(
                f"ERROR: '{path.as_posix()}' folder exists and it's not empty."
            )
    else:
        path.mkdir(parents=True)


def _is_empty(folder: Path) -> bool:
    # https://stackoverflow.com/a/54216885/14458327
    return not any(Path(folder).iterdir())


def add_zettel(config: Config) -> int:
    """Adds zettel and commits changes with zettel title as the message."""
    id_ = datetime.utcnow().strftime(C.ZULU_DATETIME_FORMAT)

    zettel_dir = Path(config.repo, C.ZETDIR, id_)
    zettel_dir.mkdir(parents=True, exist_ok=True)

    zettel_path = Path(zettel_dir, C.ZETTEL_FILENAME)

    with open(zettel_path, 'w+') as file:
        file.write('')

    _open_file(zettel_path, config)

    try:
        zet = zettel.get(zettel_path)
    except ValueError:
        logging.info(
            f"add: zettel creation aborted '{zettel_path.absolute()}'"
        )
        print('Adding zettel aborted, cleaning up...')
        zettel_path.unlink()
        zettel_dir.rmdir()
    else:
        _commit_zettel(config, zettel_path, zet.title)
        logging.info(f"add: zettel created '{zettel_path.absolute()}'")
        print(f'{id_} was created')
    return 0


def edit_zettel(args: Namespace, config: Config) -> int:
    """Edits zettel and commits changes with 'ED:' in the message."""
    if args.patterns:
        zet = zettel.get_from_grep(args, config)
    elif args.id is not None:
        zet = zettel.get_from_id(args.id, config.repo)
    else:
        zet = zettel.get_last(config.repo)

    _open_file(zet.path, config)

    try:
        zet = zettel.get(zet.path)
    except ValueError:
        logging.info(
            f"edit: zettel modification aborted '{zet.path.absolute()}'"
        )
        print('Editing zettel aborted, restoring the version from git...')
        call_git(config, 'restore', (zet.path.as_posix(),))
    else:
        if _file_was_modified(zet.path, config):
            output = _get_files_touched_last_commit(config).decode('utf-8')
            if output == f'{C.ZETDIR}/{zet.id}/{C.ZETTEL_FILENAME}\n':
                # If we touch the same zettel as in the last commit,
                # than we automatically squash the new changes with the
                # last commit, so the Git history can be simplified.
                call_git(config, 'add', (zet.path.as_posix(),))
                call_git(config, 'commit', ('--amend', '--no-edit'))
                print(
                    f'{zet.id} was edited and auto-squashed with the last'
                    ' commit\nForce push might be required'
                )
            else:
                _commit_zettel(
                    config,
                    zet.path,
                    _get_edit_commit_msg(zet.path, zet.title, config),
                )
                print(f'{zet.id} was edited')
        else:
            print(f"{zet.id} wasn't modified")
    return 0


def _get_files_touched_last_commit(config: Config) -> bytes:
    """Returns Git output listing files touched in the last commit."""
    return get_git_output(config, 'diff', ('--name-only', 'HEAD', 'HEAD^'))


def _get_edit_commit_msg(zettel_path: Path, title: str, config: Config) -> str:
    if _was_committed_to_git(zettel_path, config):
        return f'ED: {title}'
    return title


def _was_committed_to_git(filepath: Path, config: Config) -> bool:
    """Returns True if a file was committed to git.

    If 'git log' output is empty, the file wasn't committed.
    """
    return get_git_output(config, 'log', (filepath.as_posix(),)) != b''


def _file_was_modified(filepath: Path, config: Config) -> bool:
    """Returns True if a file was modified in a working dir."""
    # Run 'git add' to avoid false negatives, as 'git diff --staged' is
    # used for detection. This is important when there are external
    # factors that impact the committing process (like pre-commit).
    call_git(config, 'add', (filepath.as_posix(),))

    git_diff_out = get_git_output(
        config, 'diff', ('--staged', filepath.as_posix())
    )
    # If 'git diff' output is empty, the file wasn't modified.
    return git_diff_out != b''


def _open_file(filename: Path, config: Config) -> None:
    editor_path = Path(config.editor).expanduser().as_posix()
    if shutil.which(editor_path) is None:
        raise SystemExit(f"ERROR: editor '{editor_path}' cannot be found.")
    try:
        cmd = (config.editor, *config.editor_args, filename.as_posix())
        subprocess.run(cmd)
    except FileNotFoundError:
        raise SystemExit(
            f'ERROR: cannot open {filename.as_posix()} with {editor_path}.'
        )


def remove_zettel(args: Namespace, config: Config) -> int:
    """Removes zettel and commits changes with 'RM:' in the message."""
    if args.patterns:
        zet = zettel.get_from_grep(args, config)
    elif args.id is not None:
        zet = zettel.get_from_id(args.id, config.repo)
    else:
        raise SystemExit
    prompt = (
        f'{zet.id} will be deleted including all files '
        'that might be inside. Are you sure? (y/N): '
    )
    if input(prompt) != 'y':
        raise SystemExit('aborting')

    # All files in given zettel folder are removed one by one. This
    # might be slower than shutil.rmtree() but gives nice log entry for
    # each file.
    for file in zet.path.parent.iterdir():
        file.unlink()
        logging.info(f"remove: delete '{file}'")
        print(f'{file} was removed')

    _commit_zettel(config, zet.path, f'RM: {zet.title}')

    # If dir is removed before committing, git raises a warning that dir
    # doesn't exist.
    zet.path.parent.rmdir()
    logging.info(f"remove: delete folder '{zet.path.parent}'")
    print(f'{zet.id} was removed')

    return 0


def _commit_zettel(config: Config, zettel_path: Path, message: str) -> None:
    call_git(config, 'add', (zettel_path.as_posix(),))
    call_git(config, 'commit', ('-m', message))
    logging.info(
        f"_commit_zettel: committed '{zettel_path.absolute()}'"
        " with message '{message}'"
    )
