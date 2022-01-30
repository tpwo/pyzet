from __future__ import annotations

import argparse
import io
import itertools
import logging
import shutil
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

import pyzet.constants as const
from pyzet.sample_config import sample_config
from pyzet.zettel import get_zettel, get_zettels


@dataclass
class Config:
    repo: Path
    editor: str
    git: str


def main(argv: list[str] | None = None) -> int:
    _configure_console_print_utf8()
    logging.basicConfig(level=logging.INFO)

    parser = _get_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_usage()
        return 0
    return _parse_args(args)


def _configure_console_print_utf8() -> None:
    # https://stackoverflow.com/a/60634040/14458327
    if isinstance(sys.stdout, io.TextIOWrapper):
        # If statement is needed to satisfy mypy:
        # https://github.com/python/typeshed/issues/3049
        sys.stdout.reconfigure(encoding="utf-8")


def _get_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyzet", formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-r", "--repo", help="path to point to any zet repo")
    parser.add_argument(
        "-c",
        "--config",
        default=const.DEFAULT_CFG_LOCATION,
        help="path to alternate config file",
    )

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {const.VERSION}",
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

    list_parser = subparsers.add_parser("list", help="list zettels in given repo")
    list_parser.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="use prettier format for printing date and time",
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

    grep_parser = subparsers.add_parser("grep", help="run `git grep -niI` in zet repo")
    grep_parser.add_argument(
        "pattern",
        nargs=1,
        help="grep pattern, letter case is ignored",
    )

    status_parser = subparsers.add_parser("status", help="run `git status` in zet repo")
    _add_git_cmd_options(status_parser, "status")

    subparsers.add_parser("pull", help="run `git pull --rebase` in zet repo")

    push_parser = subparsers.add_parser("push", help="run `git push` in zet repo")
    _add_git_cmd_options(push_parser, "push")

    subparsers.add_parser(
        "sample-config", help=f"Produce a sample {const.CONFIG_FILE} file"
    )

    return parser


def _add_git_cmd_options(parser: ArgumentParser, cmd_name: str) -> None:
    parser.add_argument(
        "options",
        action="store",
        type=str,
        nargs="*",
        default=[],
        help=f"`git {cmd_name}` options, use `--` before including them",
    )


def _parse_args(args: Namespace) -> int:
    if args.command == "sample-config":
        return sample_config()
    config = _get_config(args.config, args.repo, args.command)
    id_: str | None
    try:
        # `show` & `edit` commands use nargs="?" which makes
        # args.command str rather than single element list.
        if args.command in ("show", "edit"):
            id_ = args.id
        else:
            id_ = args.id[0]
    except AttributeError:
        pass  # command that doesn't use `id` was executed
    else:
        return _parse_args_with_id(id_, args.command, config)
    return _parse_args_without_id(args, config)


def _get_config(config_file: str, args_repo_path: str, command: str) -> Config:
    """Gets config from YAML."""
    try:
        with open(config_file) as file:
            yaml_cfg = yaml.safe_load(file)
    except FileNotFoundError:
        raise SystemExit(
            f"ERROR: config file at `{Path(config_file).as_posix()}` "
            "not found.\nAdd it or use `--config` flag."
        )
    config = process_yaml(yaml_cfg, config_file, args_repo_path)
    if command == "init":  # if we initialize repo, the folder may not exist
        return config
    if not config.repo.is_dir():
        raise SystemExit(
            "ERROR: wrong repo path. "
            "Run `pyzet init` to create a git repo at "
            f"`{config.repo}`, or use `--repo` flag."
        )
    return config


def process_yaml(
    yaml_cfg: dict[str, str], config_file: str, repo_path: str | None = None
) -> Config:
    """Processes YAML config file.

    Only `repo` field is required. If other fields are missing,
    a default value will be used.
    """
    try:
        repo = Path(repo_path) if repo_path else Path(yaml_cfg["repo"]).expanduser()
    except KeyError:
        raise SystemExit(
            f"ERROR: field `repo` missing from `{Path(config_file).as_posix()}`."
        )
    editor = yaml_cfg["editor"] if yaml_cfg.get("editor") else const.VIM_PATH
    git = yaml_cfg["git"] if yaml_cfg.get("git") else const.GIT_PATH

    return Config(
        repo=repo,
        editor=editor,
        git=git,
    )


def _parse_args_with_id(id_: str | None, command: str, config: Config) -> int:
    if id_ is None:
        id_ = _get_last_zettel_id(config.repo)

    _validate_id(id_, command, config)

    if command == "show":
        return show_zettel(id_, config.repo)

    if command == "edit":
        return edit_zettel(id_, config, config.editor)

    if command == "rm":
        return remove_zettel(id_, config)

    raise NotImplementedError


def _get_last_zettel_id(repo_path: Path) -> str:
    return get_zettels(Path(repo_path, const.ZETDIR), is_reversed=True)[0].id_


def _parse_args_without_id(args: Namespace, config: Config) -> int:
    if args.command == "init":
        if args.path:
            config.repo = args.path
        return init_repo(config)

    if args.command == "add":
        return add_zettel(config)

    if args.command == "list":
        return list_zettels(
            config.repo, is_pretty=args.pretty, is_reversed=args.reverse
        )

    if args.command == "tags":
        if args.count:
            return count_tags(config.repo)
        return list_tags(config.repo, is_reversed=args.reverse)

    if args.command == "grep":
        return _call_git(config, "grep", ["-niI", args.pattern[0]])

    if args.command in ("status", "push"):
        return _call_git(config, args.command, args.options)

    if args.command == "pull":
        # `--rebase` is used to maintain a linear history without merges, as this
        # seems to be a reasonable approach in zet repo that is usually personal.
        return _call_git(config, "pull", ["--rebase"])

    if args.command == "clean":
        return clean_zet_repo(config.repo, is_dry_run=args.dry_run, is_force=args.force)

    raise NotImplementedError


def _validate_id(id_: str, command: str, config: Config) -> None:
    zettel_dir = Path(config.repo, const.ZETDIR, id_)
    if not zettel_dir.is_dir():
        raise SystemExit(f"ERROR: folder {id_} doesn't exist")
    if not Path(zettel_dir, const.ZETTEL_FILENAME).is_file():
        if command == "rm":
            raise SystemExit(
                f"ERROR: {const.ZETTEL_FILENAME} in {id_} doesn't exist. "
                "Use `pyzet clean` to remove empty folder"
            )
        raise SystemExit(f"ERROR: {const.ZETTEL_FILENAME} in {id_} doesn't exist")


def list_zettels(path: Path, is_pretty: bool, is_reversed: bool) -> int:
    for zettel in get_zettels(Path(path, const.ZETDIR), is_reversed):
        representation = zettel.timestamp if is_pretty else zettel.id_
        print(f"{representation} - {zettel.title}")
    return 0


def list_tags(path: Path, is_reversed: bool) -> int:
    zettels = get_zettels(Path(path, const.ZETDIR))
    all_tags = itertools.chain(*[t for t in [z.tags for z in zettels]])

    # Chain is reverse sorted for the correct alphabetical displaying of tag counts.
    # This is because Counter's most_common() method remembers the insertion order.
    tags = Counter(sorted(all_tags, reverse=True))

    target = tags.most_common() if is_reversed else reversed(tags.most_common())
    [print(f"{occurrences}\t#{tag}") for tag, occurrences in target]
    return 0


def count_tags(path: Path) -> int:
    print(sum(len(zettel.tags) for zettel in get_zettels(Path(path, const.ZETDIR))))
    return 0


def show_zettel(id_: str, repo_path: Path) -> int:
    """Prints zettel text prepended with centered ID as a header."""
    print(f" {id_} ".center(const.ZETTEL_WIDTH, "="))
    zettel_path = Path(repo_path, const.ZETDIR, id_, const.ZETTEL_FILENAME)
    with open(zettel_path, encoding="utf-8") as file:
        print(file.read(), end="")
    return 0


def clean_zet_repo(repo_path: Path, is_dry_run: bool, is_force: bool) -> int:
    is_any_empty = False
    for folder in sorted(Path(repo_path, const.ZETDIR).iterdir(), reverse=True):
        if folder.is_dir() and _is_empty(folder):
            is_any_empty = True
            if is_force and not is_dry_run:
                print(f"deleting {folder.name}")
                folder.rmdir()
            else:
                print(f"will delete {folder.name}")
    if is_any_empty and not is_force:
        print("Use `--force` to proceed with deletion")
    return 0


def init_repo(config: Config) -> int:
    """Initializes a git repository in a given path."""
    # We create both main ZK folder, and the folder that keeps all the zettels.
    # This is split, as each one can raise an Exception,
    # and we'd like to have a nice error message in such case.
    _create_empty_folder(config.repo)
    _create_empty_folder(Path(config.repo, const.ZETDIR))
    _call_git(config, "init")
    logging.info("Git repo was initialized. Please add a remote manually.")
    return 0


def _create_empty_folder(path: Path) -> None:
    """Creates empty folder or does nothing if it exists."""
    if path.exists():
        if not path.is_dir():
            raise SystemExit(f"ERROR: `{path.as_posix()}` exists and is a file.")
        if not _is_empty(path):
            raise SystemExit(
                f"ERROR: `{path.as_posix()}` folder exists and it's not empty."
            )
    else:
        path.mkdir(parents=True)


def _is_empty(folder: Path) -> bool:
    # https://stackoverflow.com/a/54216885/14458327
    return not any(Path(folder).iterdir())


def add_zettel(config: Config) -> int:
    """Adds zettel and commits the changes with zettel title as the commit message."""
    id_ = datetime.utcnow().strftime(const.ZULU_DATETIME_FORMAT)

    zettel_dir = Path(config.repo, const.ZETDIR, id_)
    zettel_dir.mkdir(parents=True, exist_ok=True)

    zettel_path = Path(zettel_dir, const.ZETTEL_FILENAME)

    with open(zettel_path, "w+") as file:
        file.write("")

    _open_file(zettel_path, config.editor)
    logging.info(f"{id_} was created")

    try:
        zettel = get_zettel(zettel_path.parent)
    except ValueError:
        logging.info("Adding zettel aborted, cleaning up...")
        zettel_path.unlink()
        zettel_dir.rmdir()
    else:
        _commit_zettel(config, zettel_path, zettel.title)
    return 0


def edit_zettel(id_: str, config: Config, editor: str) -> int:
    """Edits zettel and commits the changes with `ED:` in the commit message."""
    zettel_path = Path(config.repo, const.ZETDIR, id_, const.ZETTEL_FILENAME)
    _open_file(zettel_path, editor)

    try:
        zettel = get_zettel(zettel_path.parent)
    except ValueError:
        logging.info("Editing zettel aborted, restoring the version from git...")
        _call_git(config, "restore", [zettel_path.as_posix()])
    else:
        if _check_for_file_changes(zettel_path, config):
            _commit_zettel(
                config,
                zettel_path,
                _get_edit_commit_msg(zettel_path, zettel.title, config),
            )
            logging.info(f"{id_} was edited")
        else:
            logging.info(f"{id_} wasn't modified")
    return 0


def _get_edit_commit_msg(zettel_path: Path, title: str, config: Config) -> str:
    if _check_for_file_in_git(zettel_path, config):
        return f"ED: {title}"
    return title


def _check_for_file_in_git(filepath: Path, config: Config) -> bool:
    """Returns True if a file was committed to git.
    If `git log` output is empty, the file wasn't committed.
    """
    return _get_git_output(config, "log", [filepath.as_posix()]) != b""


def _check_for_file_changes(filepath: Path, config: Config) -> bool:
    """Returns True if a file was modified in a working dir."""
    # Run `git add` to avoid false negatives, as `git diff --staged` is used for
    # detection. This is important when there are external factors that impact the
    # committing process (like pre-commit).
    _call_git(config, "add", [filepath.as_posix()])

    git_diff_out = _get_git_output(config, "diff", ["--staged", filepath.as_posix()])
    # If `git diff` output is empty, the file wasn't modified.
    return git_diff_out != b""


def _open_file(filename: Path, editor: str) -> None:
    # expanduser() converts ~ into home directory
    editor_path = Path(editor).expanduser().as_posix()
    if shutil.which(editor_path) is None:
        raise SystemExit(f"ERROR: editor `{editor_path}` cannot be found.")
    try:
        subprocess.run([editor_path, filename.as_posix()])
    except FileNotFoundError:
        raise SystemExit(
            f"ERROR: cannot open {filename.as_posix()} with {editor_path}."
        )


def remove_zettel(id_: str, config: Config) -> int:
    """Removes zettel and commits the changes with `RM:` in the commit message."""
    prompt = (
        f"{id_} will be deleted including all files "
        "that might be inside. Are you sure? (y/N): "
    )
    if input(prompt) != "y":
        raise SystemExit("aborting")
    zettel_path = Path(config.repo, const.ZETDIR, id_, const.ZETTEL_FILENAME)
    zettel = get_zettel(zettel_path.parent)

    # All files in given zettel folder are removed one by one.
    # This might be slower than shutil.rmtree() but gives nice log entry for each file.
    for file in zettel_path.parent.iterdir():
        file.unlink()
        logging.info(f"{file} was removed")

    _commit_zettel(config, zettel_path, f"RM: {zettel.title}")

    # If dir is removed before committing, git raises a warning that dir doesn't exist.
    zettel_path.parent.rmdir()
    logging.info(f"{zettel_path.parent} was removed")

    return 0


def _commit_zettel(config: Config, zettel_path: Path, message: str) -> None:
    _call_git(config, "add", [zettel_path.as_posix()])
    _call_git(config, "commit", ["-m", message])


def _call_git(config: Config, command: str, options: list[str] | None = None) -> int:
    if options is None:
        options = []
    subprocess.run(
        [_get_git_cmd(config.git), "-C", config.repo.as_posix(), command, *options]
    )
    return 0


def _get_git_output(config: Config, command: str, options: list[str]) -> bytes:
    return subprocess.run(
        [_get_git_cmd(config.git), "-C", config.repo.as_posix(), command, *options],
        capture_output=True,
        check=True,
    ).stdout


def _get_git_cmd(git_path: str) -> str:
    git = Path(git_path).expanduser().as_posix()
    if shutil.which(git) is None:
        raise SystemExit(f"ERROR: `{git}` cannot be found.")
    return git
