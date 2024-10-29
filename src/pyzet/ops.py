"""Logic for handling top-level user's operations.

These operations should either return 0 if successful, or raise
SystemExit if something goes wrong.
"""

from __future__ import annotations

import itertools
import logging
import shutil
import subprocess
from collections import Counter
from datetime import datetime
from datetime import timezone
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING

import pyzet.constants as const
from pyzet import show
from pyzet import zettel
from pyzet.config import Config
from pyzet.exceptions import NotEnteredError
from pyzet.exceptions import NotFoundError
from pyzet.utils import call_git
from pyzet.utils import get_git_output
from pyzet.utils import get_git_remote_url

if TYPE_CHECKING:
    from pyzet.cli import AppState
    from pyzet.config import Config


def decide_whats_next(args: AppState, config: Config) -> None:
    """Decides what to do after finishing a command.

    This function is intended to be called recursively, so it keeps the
    state of the program and input arguments intact.
    """
    # TODO: how to enable user to switch pretty, tags &
    # show_cmd during the session
    # https://github.com/tpwo/pyzet/issues/61
    while True:
        try:
            choice = input("What's next? [p,e,d,g,G,a,q,?] ")
        except KeyboardInterrupt as err:
            raise SystemExit('\naborting') from err
        else:
            try:
                _decide(choice, args, config)
            except NotFoundError:
                logging.debug('decide_whats_next: NotFound')
                args.id = None
                args.patterns = []
            except NotEnteredError:
                # Presents the users list of found notes, as patterns
                # are not nullified
                logging.debug('decide_whats_next: NotEntered')
                args.id = None


def _decide(choice: str, args: AppState, config: Config) -> None:
    if choice == 'p':
        show.command(args, config)
    elif choice == 'e':
        edit_zettel(args, config)
    elif choice == 'd':
        remove_zettel(args, config)
    elif choice in {'g', 'G'}:
        args.show_cmd = 'text'
        args.id = None
        args.ignore_case = choice == 'G'
        args.patterns = _get_grep_patterns()
        matches = zettel.get_from_grep(args, config)
        print(f'Found {len(matches)} matches')
    elif choice == 'a':
        add_zettel(args, config)
    elif choice == 'q':
        raise SystemExit('Bye!')
    elif choice == '?':
        print(_get_help_msg(args), end='')
    else:  # By default print the note again.
        pass


def _get_grep_patterns() -> list[str]:
    try:
        patterns = input('Grep patterns: ').split()
    except KeyboardInterrupt as err:
        print('\ncancelled, press again to quit')
        raise NotEnteredError from err
    else:
        return patterns


def _get_help_msg(args: AppState) -> str:
    help_msg_with_id = """\
p - print current note
e - edit current note
d - delete current note
g - grep for other notes
G - grep for other notes (case insensitive)
a - add a new note
q - quit
? - print help
"""
    help_msg_with_patterns = """\
p - print one of matching notes
e - edit one of matching notes
d - delete one of matching notes
g - grep for other notes
G - grep for other notes (case insensitive)
a - add a new note
q - quit
? - print help
"""
    status = f"""
current ID: {args.id}
patterns: {args.patterns}
"""
    help_msg = help_msg_with_id if args.id else help_msg_with_patterns
    return help_msg + ''.center(27, '-') + status


def get_remote_url(args: AppState, config: Config) -> None:
    print(get_git_remote_url(config, args.name))


def list_zettels(args: AppState, path: Path) -> None:
    for zet in zettel.get_all(
        Path(path, const.ZETDIR), is_reversed=args.reverse
    ):
        print(zettel.get_repr(zet, args))


def clean_zet_repo(
    repo_path: Path, *, is_dry_run: bool, is_force: bool
) -> None:
    is_any_empty = False
    for folder in sorted(
        Path(repo_path, const.ZETDIR).iterdir(), reverse=True
    ):
        if folder.is_dir() and _is_empty(folder):
            is_any_empty = True
            if is_force and not is_dry_run:
                print(f'deleting {folder.name}')
                folder.rmdir()
            else:
                print(f'will delete {folder.name}')
    if is_any_empty and not is_force:
        print("use '--force' to proceed with deletion")


def init_repo(config: Config, branch_name: str) -> None:
    """Initialize a git repository in a given path."""
    # We create both main ZK folder, and the folder that keeps all the
    # zettels. This is split, as each one can raise an Exception, and
    # we'd like to have a nice error message in such case.
    _create_empty_folder(config.repo)
    _create_empty_folder(Path(config.repo, const.ZETDIR))
    call_git(config, 'init', ('--initial-branch', branch_name))
    logging.info(f"init: create git repo '{config.repo.absolute()}'")


def _create_empty_folder(path: Path) -> None:
    """Create empty folder or does nothing if it exists."""
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


def add_zettel(args: AppState, config: Config) -> None:
    """Add zettel and commits changes with zettel title as the message."""
    id_ = datetime.now(tz=timezone.utc).strftime(const.ZULU_DATETIME_FORMAT)

    zettel_dir = Path(config.repo, const.ZETDIR, id_)
    zettel_dir.mkdir(parents=True, exist_ok=True)

    zettel_path = Path(zettel_dir, const.ZETTEL_FILENAME)

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
        args.id = id_


def edit_zettel(args: AppState, config: Config) -> None:
    """Edits zettel and commits changes with 'ED:' in the message."""
    if args.id is not None:
        zet = zettel.get_from_id(args.id, config.repo)
    elif args.patterns:
        zet = zettel.select_from_grep(args, config)
    else:
        zet = zettel.get_last(config.repo)

    args.id = zet.id
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
            if output == f'{const.ZETDIR}/{zet.id}/{const.ZETTEL_FILENAME}\n':
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


def _get_files_touched_last_commit(config: Config) -> bytes:
    """Return Git output listing files touched in the last commit."""
    return get_git_output(config, 'diff', ('--name-only', 'HEAD', 'HEAD^'))


def _get_edit_commit_msg(zettel_path: Path, title: str, config: Config) -> str:
    if _was_committed_to_git(zettel_path, config):
        return f'ED: {title}'
    return title


def _was_committed_to_git(filepath: Path, config: Config) -> bool:
    """Return True if a file was committed to git.

    If 'git log' output is empty, the file wasn't committed.
    """
    return get_git_output(config, 'log', (filepath.as_posix(),)) != b''


def _file_was_modified(filepath: Path, config: Config) -> bool:
    """Return True if a file was modified in a working dir."""
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
    except FileNotFoundError as err:
        raise SystemExit(
            f'ERROR: cannot open {filename.as_posix()} with {editor_path}.'
        ) from err


def remove_zettel(args: AppState, config: Config) -> None:
    """Remove zettel and commits changes with 'RM:' in the message."""
    if args.id is not None:
        zet = zettel.get_from_id(args.id, config.repo)
    elif args.patterns:
        zet = zettel.select_from_grep(args, config)
    else:
        raise SystemExit
    prompt = (
        f'{zet.id} `{zet.title}` will be deleted including all files '
        'that might be inside. Are you sure? (y/N): '
    )
    try:
        if input(prompt) != 'y':
            print('aborting')
            raise NotEnteredError
    except KeyboardInterrupt:
        print('\naborting')
        raise NotEnteredError from KeyboardInterrupt

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
    args.id = None


def _commit_zettel(config: Config, zettel_path: Path, message: str) -> None:
    call_git(config, 'add', (zettel_path.as_posix(),))
    call_git(config, 'commit', ('-m', message))
    logging.info(
        f"_commit_zettel: committed '{zettel_path.absolute()}'"
        " with message '{message}'"
    )


def list_tags(repo: Path, *, is_reversed: bool) -> None:
    tags = _get_tags(repo)
    target = (
        tags.most_common() if is_reversed else reversed(tags.most_common())
    )
    print(*(f'{occurrences}\t#{tag}' for tag, occurrences in target), sep='\n')


def info(config: Config) -> None:
    """Print info about ZK repo."""
    print(_get_info(config))


def _get_info(config: Config) -> str:
    dir_ = Path(config.repo, const.ZETDIR)
    zettels = zettel.get_all(dir_)
    lines, words, bytes_ = _get_wc_output(config)
    git_size, git_size_pack = _get_git_size_stats(config)
    return f"""\
Number of notes:       {len(zettels)}
Number of lines:       {lines}
Number of words:       {words}
Number of bytes:       {bytes_}
Number of tags:        {_count_tags(config.repo)}
Number of unique tags: {len(_get_tags(config.repo))}
Size on disk:          {_bytes_to_mb(bytes_)} MiB
Git repo size:         {git_size} MiB
Git repo size-pack:    {git_size_pack} MiB\
"""


def _bytes_to_mb(bytes_: int) -> float:
    return round(bytes_ / 1024 / 1024, 2)


def _get_wc_output(config: Config) -> tuple[int, int, int]:
    """Use wc and glob to count the number of lines in md files.

    wc output shows total number of lines, words, and bytes in the last
    line, so we parse it to get out the value.
    """
    repo = config.repo.as_posix()
    files = glob(f'{repo}/{const.ZETDIR}/**/*.md', recursive=True)
    cmd = ('wc', *files)
    wc_out = subprocess.run(cmd, capture_output=True).stdout.decode().strip()
    last_line = wc_out.split('\n')[-1].strip()
    lines, words, bytes_, _ = last_line.split()
    return int(lines), int(words), int(bytes_)


def _get_tags(repo: Path) -> Counter[str]:
    zettels = zettel.get_all(Path(repo, const.ZETDIR))
    all_tags = itertools.chain.from_iterable(
        t for t in (z.tags for z in zettels)
    )
    # Chain is reverse sorted for the correct alphabetical displaying of
    # tag counts. This is because Counter's most_common() method
    # remembers the insertion order.
    return Counter(sorted(all_tags, reverse=True))


def _count_tags(repo: Path) -> int:
    dir_ = Path(repo, const.ZETDIR)
    return sum(len(zettel.tags) for zettel in zettel.get_all(dir_))


def _get_git_size_stats(config: Config) -> tuple[float, float]:
    """Run 'git count-objects -v' and parses the output.

    'size' and 'size-pack' values are returned.
    """
    git_stats = get_git_output(config, 'count-objects', ('-v',))
    git_stats_parsed = git_stats.decode().split('\n')
    size = ' '.join(git_stats_parsed[1].split()[1:])
    size_pack = ' '.join(git_stats_parsed[4].split()[1:])
    return _kb_to_mb(int(size)), _kb_to_mb(int(size_pack))


def _kb_to_mb(kb: int) -> float:
    return round(kb / 1024, 2)
