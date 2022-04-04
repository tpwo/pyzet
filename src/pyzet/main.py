from __future__ import annotations

import argparse
import functools
import itertools
import logging
import shutil
import subprocess
from argparse import ArgumentParser, Namespace
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

import pyzet.constants as C
from pyzet import utils
from pyzet.sample_config import sample_config
from pyzet.zettel import Zettel, get_zettel, get_zettels


@dataclass
class Config:
    repo: Path
    editor: str
    git: str


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
        prog="pyzet", formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-r", "--repo", help="path to point to any zet repo")
    parser.add_argument(
        "-c",
        "--config",
        default=C.DEFAULT_CFG_LOCATION,
        help="path to alternate config file",
    )

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {C.VERSION}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase verbosity of the output",
    )

    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="initialize a git ZK repository")
    init_parser.add_argument(
        "path",
        nargs="?",
        help="repo path, by default ~/zet; if target dir exists, it must be empty",
    )

    subparsers.add_parser("add", help="add a new zettel")

    edit_parser = subparsers.add_parser("edit", help="edit a zettel")
    edit_parser.add_argument(
        "id",
        nargs="?",
        help="zettel id, by default edits zettel with the newest timestamp",
    )

    remove_parser = subparsers.add_parser("rm", help="remove a zettel")
    remove_parser.add_argument("id", nargs=1, help="zettel id (timestamp)")

    show_parser = subparsers.add_parser("show", help="print zettel contents")
    show_parser.add_argument(
        "id",
        nargs="?",
        help="zettel id, by default shows zettel with the newest timestamp",
    )
    show_parser.add_argument(
        "-l",
        "--link",
        action="store_true",
        help="show zettel as a relative Markdown link",
    )

    list_parser = subparsers.add_parser("list", help="list zettels in given repo")
    list_parser.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="use prettier format for printing date and time",
    )
    list_parser.add_argument(
        "-l",
        "--link",
        action="store_true",
        help="print zettels as relative Markdown links",
    )
    list_parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="reverse the output (so the newest are first)",
    )

    tags_parser = subparsers.add_parser("tags", help="list tags in given repo")
    tags_parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="reverse the output to be descending",
    )
    tags_parser.add_argument(
        "--count",
        action="store_true",
        help="count the total number of all tags in zet repo (non-unique)",
    )

    clean_parser = subparsers.add_parser(
        "clean", help="delete empty folders in zet repo"
    )
    clean_parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="list what will be deleted, but don't delete it",
    )
    clean_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force, use it to actually delete anything",
    )

    grep_parser = subparsers.add_parser(
        "grep", help="run 'git grep' with some handy flags in zet repo"
    )
    grep_parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="case insensitive matching",
    )
    grep_parser.add_argument(
        "-t",
        "--title",
        action="store_true",
        help="add zettel title to matching lines",
    )
    grep_parser.add_argument(
        "-n",
        "--line-number",
        action="store_true",
        help="prefix the line number to matching lines",
    )
    grep_parser.add_argument(
        "patterns",
        nargs="+",
        help="grep patterns, pass 'git grep' options after '--'",
    )

    status_parser = subparsers.add_parser("status", help="run 'git status' in zet repo")
    _add_git_cmd_options(status_parser, "status")

    subparsers.add_parser("pull", help="run 'git pull --rebase' in zet repo")

    push_parser = subparsers.add_parser("push", help="run 'git push' in zet repo")
    _add_git_cmd_options(push_parser, "push")

    subparsers.add_parser(
        "sample-config", help=f"produce a sample {C.CONFIG_FILE} file"
    )

    return parser


def _add_git_cmd_options(parser: ArgumentParser, cmd_name: str) -> None:
    parser.add_argument(
        "options",
        action="store",
        type=str,
        nargs="*",
        default=[],
        help=f"pass 'git {cmd_name}' options, use '--' before including them",
    )


def _parse_args(args: Namespace) -> int:
    if args.command == "sample-config":
        return sample_config()
    config = _get_config(args.config, args.repo, args.command)
    id_: str | None
    try:
        # show & edit commands use nargs="?" which makes
        # args.command str rather than single element list.
        if args.command in ("show", "edit"):
            id_ = args.id
        else:
            id_ = args.id[0]
    except AttributeError:
        pass  # command that doesn't use 'id' was executed
    else:
        return _parse_args_with_id(id_, args, config)
    return _parse_args_without_id(args, config)


def _get_config(config_file: str, args_repo_path: str, command: str) -> Config:
    """Gets config from YAML."""
    try:
        with open(config_file) as file:
            yaml_cfg = yaml.safe_load(file)
    except FileNotFoundError:
        raise SystemExit(
            f"ERROR: config file at '{Path(config_file).as_posix()}' "
            "not found.\nAdd it or use '--config' flag."
        )
    config = process_yaml(yaml_cfg, config_file, args_repo_path)
    if command == "init":  # if we initialize repo, the folder may not exist
        return config
    if not config.repo.is_dir():
        raise SystemExit(
            "ERROR: wrong repo path. "
            "Run 'pyzet init' to create a git repo at "
            f"'{config.repo}', or use '--repo' flag."
        )
    return config


def process_yaml(
    yaml_cfg: dict[str, str], config_file: str, repo_path: str | None = None
) -> Config:
    """Processes YAML config file.

    Only 'repo' field is required. If other fields are missing,
    a default value will be used.
    """
    try:
        repo = Path(repo_path) if repo_path else Path(yaml_cfg["repo"]).expanduser()
    except KeyError:
        raise SystemExit(
            f"ERROR: field 'repo' missing from '{Path(config_file).as_posix()}'."
        )
    return Config(
        repo=repo,
        editor=_get_config_option(yaml_cfg, "editor", C.VIM_PATH),
        git=_get_config_option(yaml_cfg, "git", C.GIT_PATH),
    )


def _get_config_option(yaml_cfg: dict[str, str], option: str, default: str) -> str:
    if yaml_cfg.get(option):
        value = yaml_cfg[option]
        logging.debug(f"_get_config_option: {option} '{value}' found in YAML")
        return value
    else:
        logging.debug(f"_get_config_option: using default {option} '{default}'")
        return default


def _parse_args_with_id(id_: str | None, args: Namespace, config: Config) -> int:
    if id_ is None:
        id_ = _get_last_zettel_id(config.repo)

    command = args.command
    _validate_id(id_, command, config)

    if command == "show":
        if args.link:
            return show_zettel_as_md_link(id_, config.repo)
        return show_zettel(id_, config.repo)

    if command == "edit":
        return edit_zettel(id_, config, config.editor)

    if command == "rm":
        return remove_zettel(id_, config)

    raise NotImplementedError


def _get_last_zettel_id(repo_path: Path) -> str:
    return get_zettels(Path(repo_path, C.ZETDIR), is_reversed=True)[0].id_


def _parse_args_without_id(args: Namespace, config: Config) -> int:
    if args.command == "init":
        if args.path:
            config.repo = args.path
        return init_repo(config)

    if args.command == "add":
        return add_zettel(config)

    if args.command == "list":
        return list_zettels(
            config.repo,
            is_pretty=args.pretty,
            is_link=args.link,
            is_reverse=args.reverse,
        )

    if args.command == "tags":
        if args.count:
            return count_tags(config.repo)
        return list_tags(config.repo, is_reversed=args.reverse)

    if args.command == "grep":
        grep_opts = _build_grep_options(args.ignore_case, args.line_number, args.title)
        patterns = _parse_grep_patterns(args.patterns)
        grep_opts.extend(patterns)
        return _call_git(
            config,
            "grep",
            grep_opts,
            path=Path(config.repo, C.ZETDIR),
        )

    if args.command in ("status", "push"):
        return _call_git(config, args.command, args.options)

    if args.command == "pull":
        # --rebase is used to maintain a linear history without merges, as this
        # seems to be a reasonable approach in zet repo that is usually personal.
        return _call_git(config, "pull", ["--rebase"])

    if args.command == "clean":
        return clean_zet_repo(config.repo, is_dry_run=args.dry_run, is_force=args.force)

    raise NotImplementedError


def _build_grep_options(ignore_case: bool, line_number: bool, title: bool) -> list[str]:
    opts = [
        "-I",
        "--heading",
        "--break",
        "--all-match",
    ]
    if ignore_case:
        opts.append("--ignore-case")
    if line_number:
        opts.append("--line-number")
    if title:
        zettel_title_pattern = r"^#\s.*"
        opts.extend(_add_git_grep_pattern(zettel_title_pattern))
    return opts


def _parse_grep_patterns(patterns: list[str]) -> list[str]:
    opts = []
    for idx, pat in enumerate(patterns):
        if pat.startswith("-"):
            # Flags started appearing, so there is no more patterns
            opts.extend(patterns[idx:])
            break
        opts.extend(_add_git_grep_pattern(pat))
    return opts


def _add_git_grep_pattern(pattern: str) -> tuple[str, str, str]:
    """Uses 'git grep' syntax for including multiple patterns.

    This approach works only with --all-match, i.e. only a file that
    includes all of patterns will be matched.
    """
    return "--or", "-e", pattern


def _validate_id(id_: str, command: str, config: Config) -> None:
    zettel_dir = Path(config.repo, C.ZETDIR, id_)
    if not zettel_dir.is_dir():
        raise SystemExit(f"ERROR: folder {id_} doesn't exist")
    if not Path(zettel_dir, C.ZETTEL_FILENAME).is_file():
        if command == "rm":
            raise SystemExit(
                f"ERROR: {C.ZETTEL_FILENAME} in {id_} doesn't exist. "
                "Use 'pyzet clean' to remove empty folder"
            )
        raise SystemExit(f"ERROR: {C.ZETTEL_FILENAME} in {id_} doesn't exist")


def list_zettels(path: Path, is_pretty: bool, is_link: bool, is_reverse: bool) -> int:
    for zettel in get_zettels(Path(path, C.ZETDIR), is_reverse):
        print(_get_zettel_repr(zettel, is_pretty, is_link))
    return 0


def _get_zettel_repr(zettel: Zettel, is_pretty: bool, is_link: bool) -> str:
    if is_pretty:
        return f"{zettel.timestamp} -- {zettel.title}"
    if is_link:
        return _get_md_relative_link(zettel.id_, zettel.title)
    return f"{zettel.id_} -- {zettel.title}"


def list_tags(path: Path, is_reversed: bool) -> int:
    zettels = get_zettels(Path(path, C.ZETDIR))
    all_tags = itertools.chain(*[t for t in [z.tags for z in zettels]])

    # Chain is reverse sorted for the correct alphabetical displaying of tag counts.
    # This is because Counter's most_common() method remembers the insertion order.
    tags = Counter(sorted(all_tags, reverse=True))

    target = tags.most_common() if is_reversed else reversed(tags.most_common())
    [print(f"{occurrences}\t#{tag}") for tag, occurrences in target]
    return 0


def count_tags(path: Path) -> int:
    print(sum(len(zettel.tags) for zettel in get_zettels(Path(path, C.ZETDIR))))
    return 0


def show_zettel(id_: str, repo_path: Path) -> int:
    """Prints zettel text prepended with centered ID as a header."""
    print(f" {id_} ".center(C.ZETTEL_WIDTH, "="))
    zettel_path = Path(repo_path, C.ZETDIR, id_, C.ZETTEL_FILENAME)
    with open(zettel_path, encoding="utf-8") as file:
        print(file.read(), end="")
    return 0


def show_zettel_as_md_link(id_: str, repo_path: Path) -> int:
    zettel_path = Path(repo_path, C.ZETDIR, id_)
    zettel = get_zettel(zettel_path)
    print(_get_md_relative_link(zettel.id_, zettel.title))
    return 0


def _get_md_relative_link(id_: str, title: str) -> str:
    """Returns a representation of a zettel that is a relative Markdown link.

    Asterix at the beginning is a Markdown syntax for an unordered list, as links to
    zettels are usually just used in references section of a zettel.
    """
    return f"* [{id_}](../{id_}) -- {title}"


def clean_zet_repo(repo_path: Path, is_dry_run: bool, is_force: bool) -> int:
    is_any_empty = False
    for folder in sorted(Path(repo_path, C.ZETDIR).iterdir(), reverse=True):
        if folder.is_dir() and _is_empty(folder):
            is_any_empty = True
            if is_force and not is_dry_run:
                print(f"deleting {folder.name}")
                folder.rmdir()
            else:
                print(f"will delete {folder.name}")
    if is_any_empty and not is_force:
        print("Use '--force' to proceed with deletion")
    return 0


def init_repo(config: Config) -> int:
    """Initializes a git repository in a given path."""
    # We create both main ZK folder, and the folder that keeps all the zettels.
    # This is split, as each one can raise an Exception,
    # and we'd like to have a nice error message in such case.
    _create_empty_folder(config.repo)
    _create_empty_folder(Path(config.repo, C.ZETDIR))
    _call_git(config, "init")
    logging.info(f"init: create git repo '{config.repo.absolute()}'")
    print("Git repo was initialized. Please add a remote manually.")
    return 0


def _create_empty_folder(path: Path) -> None:
    """Creates empty folder or does nothing if it exists."""
    if path.exists():
        if not path.is_dir():
            raise SystemExit(f"ERROR: '{path.as_posix()}' exists and is a file.")
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
    """Adds zettel and commits the changes with zettel title as the commit message."""
    id_ = datetime.utcnow().strftime(C.ZULU_DATETIME_FORMAT)

    zettel_dir = Path(config.repo, C.ZETDIR, id_)
    zettel_dir.mkdir(parents=True, exist_ok=True)

    zettel_path = Path(zettel_dir, C.ZETTEL_FILENAME)

    with open(zettel_path, "w+") as file:
        file.write("")

    _open_file(zettel_path, config.editor)

    try:
        zettel = get_zettel(zettel_path.parent)
    except ValueError:
        logging.info(f"add: zettel creation aborted '{zettel_path.absolute()}'")
        print("Adding zettel aborted, cleaning up...")
        zettel_path.unlink()
        zettel_dir.rmdir()
    else:
        _commit_zettel(config, zettel_path, zettel.title)
        logging.info(f"add: zettel created '{zettel_path.absolute()}'")
        print(f"{id_} was created")
    return 0


def edit_zettel(id_: str, config: Config, editor: str) -> int:
    """Edits zettel and commits the changes with 'ED:' in the commit message."""
    zettel_path = Path(config.repo, C.ZETDIR, id_, C.ZETTEL_FILENAME)
    _open_file(zettel_path, editor)

    try:
        zettel = get_zettel(zettel_path.parent)
    except ValueError:
        logging.info(f"edit: zettel modification aborted '{zettel_path.absolute()}'")
        print("Editing zettel aborted, restoring the version from git...")
        _call_git(config, "restore", [zettel_path.as_posix()])
    else:
        if _check_for_file_changes(zettel_path, config):
            _commit_zettel(
                config,
                zettel_path,
                _get_edit_commit_msg(zettel_path, zettel.title, config),
            )
            logging.info(f"edit: zettel modified '{zettel_path.absolute()}'")
            print(f"{id_} was edited")
        else:
            logging.info(f"edit: zettel not modified '{zettel_path.absolute()}'")
            print(f"{id_} wasn't modified")
    return 0


def _get_edit_commit_msg(zettel_path: Path, title: str, config: Config) -> str:
    if _check_for_file_in_git(zettel_path, config):
        return f"ED: {title}"
    return title


def _check_for_file_in_git(filepath: Path, config: Config) -> bool:
    """Returns True if a file was committed to git.
    If 'git log' output is empty, the file wasn't committed.
    """
    return _get_git_output(config, "log", [filepath.as_posix()]) != b""


def _check_for_file_changes(filepath: Path, config: Config) -> bool:
    """Returns True if a file was modified in a working dir."""
    # Run 'git add' to avoid false negatives, as 'git diff --staged' is used for
    # detection. This is important when there are external factors that impact the
    # committing process (like pre-commit).
    _call_git(config, "add", [filepath.as_posix()])

    git_diff_out = _get_git_output(config, "diff", ["--staged", filepath.as_posix()])
    # If 'git diff' output is empty, the file wasn't modified.
    return git_diff_out != b""


def _open_file(filename: Path, editor: str) -> None:
    # expanduser() converts ~ into home directory
    editor_path = Path(editor).expanduser().as_posix()
    if shutil.which(editor_path) is None:
        raise SystemExit(f"ERROR: editor '{editor_path}' cannot be found.")
    try:
        subprocess.run([editor_path, filename.as_posix()])
    except FileNotFoundError:
        raise SystemExit(
            f"ERROR: cannot open {filename.as_posix()} with {editor_path}."
        )


def remove_zettel(id_: str, config: Config) -> int:
    """Removes zettel and commits the changes with 'RM:' in the commit message."""
    prompt = (
        f"{id_} will be deleted including all files "
        "that might be inside. Are you sure? (y/N): "
    )
    if input(prompt) != "y":
        raise SystemExit("aborting")
    zettel_path = Path(config.repo, C.ZETDIR, id_, C.ZETTEL_FILENAME)
    zettel = get_zettel(zettel_path.parent)

    # All files in given zettel folder are removed one by one.
    # This might be slower than shutil.rmtree() but gives nice log entry for each file.
    for file in zettel_path.parent.iterdir():
        file.unlink()
        logging.info(f"remove: delete '{file}'")
        print(f"{file} was removed")

    _commit_zettel(config, zettel_path, f"RM: {zettel.title}")

    # If dir is removed before committing, git raises a warning that dir doesn't exist.
    zettel_path.parent.rmdir()
    logging.info(f"remove: delete folder '{zettel_path.parent}'")
    print(f"{zettel_path.parent} was removed")

    return 0


def _commit_zettel(config: Config, zettel_path: Path, message: str) -> None:
    _call_git(config, "add", [zettel_path.as_posix()])
    _call_git(config, "commit", ["-m", message])
    logging.info(
        f"_commit_zettel: committed '{zettel_path.absolute()}' with message '{message}'"
    )


def _call_git(
    config: Config,
    command: str,
    options: list[str] | None = None,
    path: Path | None = None,
) -> int:
    if options is None:
        options = []
    if path is None:
        path = config.repo
    cmd = [_get_git_cmd(config.git), "-C", path.as_posix(), command, *options]
    logging.debug(f"_call_git: subprocess.run({cmd})")
    subprocess.run(cmd)
    return 0


def _get_git_output(config: Config, command: str, options: list[str]) -> bytes:
    cmd = [_get_git_cmd(config.git), "-C", config.repo.as_posix(), command, *options]
    logging.debug(f"_get_git_output: subprocess.run({cmd})")
    return subprocess.run(cmd, capture_output=True, check=True).stdout


@functools.lru_cache(maxsize=1)
def _get_git_cmd(git_path: str) -> str:
    git = Path(git_path).expanduser().as_posix()
    if shutil.which(git) is None:
        raise SystemExit(f"ERROR: '{git}' cannot be found.")
    logging.debug(f"_get_git_cmd: found at '{git}'")
    return git
