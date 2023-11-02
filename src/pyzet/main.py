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
from pyzet import utils
from pyzet.grep import define_grep_cli
from pyzet.grep import grep
from pyzet.sample_config import define_sample_config_cli
from pyzet.sample_config import sample_config
from pyzet.utils import call_git
from pyzet.utils import Config
from pyzet.utils import get_git_output
from pyzet.zettel import get_timestamp
from pyzet.zettel import get_zettel
from pyzet.zettel import get_zettels
from pyzet.zettel import Zettel


def main(argv: list[str] | None = None) -> int:
    utils.configure_console_print_utf8()

    parser = _get_parser()
    args = parser.parse_args(argv)
    utils.setup_logger(utils.compute_log_level(args.verbose))

    if args.command is None:
        parser.print_usage()
        return 0
    return _parse_args(args)


def _get_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='pyzet', formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-r', '--repo', help='point to a custom ZK repo')
    parser.add_argument(
        '-c',
        '--config',
        default=C.DEFAULT_CFG_LOCATION,
        help='use an alternative config file',
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
        nargs='?',
        default='main',
        help="override the name of the initial branch, by default 'main'",
    )

    subparsers.add_parser('add', help='add a new zettel')

    edit_parser = subparsers.add_parser('edit', help='edit an existing zettel')
    edit_parser.add_argument(
        'id',
        nargs='?',
        help='zettel id, defaults to zettel with the newest timestamp',
    )

    remove_parser = subparsers.add_parser('rm', help='remove a zettel')
    remove_parser.add_argument('id', nargs=1, help='zettel id (timestamp)')

    show_parser = subparsers.add_parser('show', help='print zettel contents')
    show_parser.add_argument(
        'id',
        nargs='?',
        help='zettel id, defaults to zettel with the newest timestamp',
    )
    show_parser.add_argument(
        '-l',
        '--link',
        action='store_true',
        help='show zettel as a relative Markdown'
        ' link for pasting in other zettels',
    )

    list_parser = subparsers.add_parser('list', help='list all zettels')
    list_parser.add_argument(
        '-p',
        '--pretty',
        action='store_true',
        help='use prettier format for printing date and time',
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
        'remote', help="run 'git remote -v' in ZK repo"
    )
    _add_git_cmd_options(remote_parser, 'remote')

    define_sample_config_cli(subparsers)

    return parser


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
    id_: str | None
    try:
        # show & edit commands use nargs="?" which makes
        # args.command str rather than single element list.
        if args.command in {'show', 'edit'}:
            id_ = args.id
        else:
            id_ = args.id[0]
    except AttributeError:
        pass  # command that doesn't use 'id' was executed
    else:
        return _parse_args_with_id(id_, args, config)
    return _parse_args_without_id(args, config)


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


def _parse_args_with_id(
    id_: str | None, args: Namespace, config: Config
) -> int:
    if id_ is None:
        id_ = _get_last_zettel_id(config.repo)

    command = args.command
    _validate_id(id_, command, config)

    if command == 'show':
        if args.link:
            return show_zettel_as_md_link(id_, config.repo)
        return show_zettel(id_, config.repo)

    if command == 'edit':
        return edit_zettel(id_, config, config.editor)

    if command == 'rm':
        return remove_zettel(id_, config)

    raise NotImplementedError


def _get_last_zettel_id(repo_path: Path) -> str:
    return get_zettels(Path(repo_path, C.ZETDIR), is_reversed=True)[0].id_


def _parse_args_without_id(args: Namespace, config: Config) -> int:
    if args.command == 'init':
        return init_repo(config, args.initial_branch)

    if args.command == 'add':
        return add_zettel(config)

    if args.command == 'list':
        return list_zettels(
            config.repo,
            is_pretty=args.pretty,
            is_link=args.link,
            is_reverse=args.reverse,
        )

    if args.command == 'tags':
        if args.count:
            return count_tags(config.repo)
        return list_tags(config.repo, is_reversed=args.reverse)

    if args.command == 'grep':
        return grep(args, config)

    if args.command in {'status', 'push'}:
        return call_git(config, args.command, args.options)

    if args.command == 'remote':
        return call_git(config, 'remote', ('-v', *args.options))

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


def _validate_id(id_: str, command: str, config: Config) -> None:
    zettel_dir = Path(config.repo, C.ZETDIR, id_)
    if not zettel_dir.is_dir():
        raise SystemExit(f"ERROR: folder {id_} doesn't exist")
    if not Path(zettel_dir, C.ZETTEL_FILENAME).is_file():
        if command == 'rm':
            raise SystemExit(
                f"ERROR: {C.ZETTEL_FILENAME} in {id_} doesn't exist. "
                "Use 'pyzet clean' to remove empty folder"
            )
        raise SystemExit(f"ERROR: {C.ZETTEL_FILENAME} in {id_} doesn't exist")


def list_zettels(
    path: Path, is_pretty: bool, is_link: bool, is_reverse: bool
) -> int:
    for zettel in get_zettels(Path(path, C.ZETDIR), is_reverse):
        print(_get_zettel_repr(zettel, is_pretty, is_link))
    return 0


def _get_zettel_repr(zettel: Zettel, is_pretty: bool, is_link: bool) -> str:
    if is_pretty:
        return f'{get_timestamp(zettel.id_)} -- {zettel.title}'
    if is_link:
        return _get_md_relative_link(zettel.id_, zettel.title)
    return f'{zettel.id_} -- {zettel.title}'


def list_tags(path: Path, is_reversed: bool) -> int:
    zettels = get_zettels(Path(path, C.ZETDIR))
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
    print(
        sum(len(zettel.tags) for zettel in get_zettels(Path(path, C.ZETDIR)))
    )
    return 0


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
    print(_get_md_relative_link(zettel.id_, zettel.title))
    return 0


def _get_md_relative_link(id_: str, title: str) -> str:
    """Returns a representation of a zettel that is a relative Markdown link.

    Asterisk at the beginning is a Markdown syntax for an unordered list,
    as links to zettels are usually just used in references section of a
    zettel.
    """
    return f'* [{id_}](../{id_}) {title}'


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
        zettel = get_zettel(zettel_path.parent)
    except ValueError:
        logging.info(
            f"add: zettel creation aborted '{zettel_path.absolute()}'"
        )
        print('Adding zettel aborted, cleaning up...')
        zettel_path.unlink()
        zettel_dir.rmdir()
    else:
        _commit_zettel(config, zettel_path, zettel.title)
        logging.info(f"add: zettel created '{zettel_path.absolute()}'")
        print(f'{id_} was created')
    return 0


def edit_zettel(id_: str, config: Config, editor: str) -> int:
    """Edits zettel and commits changes with 'ED:' in the message."""
    zettel_path = Path(config.repo, C.ZETDIR, id_, C.ZETTEL_FILENAME)
    _open_file(zettel_path, config)

    try:
        zettel = get_zettel(zettel_path.parent)
    except ValueError:
        logging.info(
            f"edit: zettel modification aborted '{zettel_path.absolute()}'"
        )
        print('Editing zettel aborted, restoring the version from git...')
        call_git(config, 'restore', (zettel_path.as_posix(),))
    else:
        if _file_was_modified(zettel_path, config):
            output = _get_files_touched_last_commit(config).decode('utf-8')
            if output == f'{C.ZETDIR}/{id_}/{C.ZETTEL_FILENAME}\n':
                # If we touch the same zettel as in the last commit,
                # than we automatically squash the new changes with the
                # last commit, so the Git history can be simplified.
                call_git(config, 'add', (zettel_path.as_posix(),))
                call_git(config, 'commit', ('--amend', '--no-edit'))
                print(
                    f'{id_} was edited and auto-squashed with the last commit'
                    '\nForce push might be required'
                )
            else:
                _commit_zettel(
                    config,
                    zettel_path,
                    _get_edit_commit_msg(zettel_path, zettel.title, config),
                )
                print(f'{id_} was edited')
        else:
            print(f"{id_} wasn't modified")
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


def remove_zettel(id_: str, config: Config) -> int:
    """Removes zettel and commits changes with 'RM:' in the message."""
    prompt = (
        f'{id_} will be deleted including all files '
        'that might be inside. Are you sure? (y/N): '
    )
    if input(prompt) != 'y':
        raise SystemExit('aborting')
    zettel_path = Path(config.repo, C.ZETDIR, id_, C.ZETTEL_FILENAME)
    zettel = get_zettel(zettel_path.parent)

    # All files in given zettel folder are removed one by one. This
    # might be slower than shutil.rmtree() but gives nice log entry for
    # each file.
    for file in zettel_path.parent.iterdir():
        file.unlink()
        logging.info(f"remove: delete '{file}'")
        print(f'{file} was removed')

    _commit_zettel(config, zettel_path, f'RM: {zettel.title}')

    # If dir is removed before committing, git raises a warning that dir
    # doesn't exist.
    zettel_path.parent.rmdir()
    logging.info(f"remove: delete folder '{zettel_path.parent}'")
    print(f'{zettel_path.parent} was removed')

    return 0


def _commit_zettel(config: Config, zettel_path: Path, message: str) -> None:
    call_git(config, 'add', (zettel_path.as_posix(),))
    call_git(config, 'commit', ('-m', message))
    logging.info(
        f"_commit_zettel: committed '{zettel_path.absolute()}'"
        " with message '{message}'"
    )
