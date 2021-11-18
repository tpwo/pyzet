from __future__ import annotations

import argparse
import io
import logging
import shutil
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pyzet.constants as const
from pyzet.zettel import get_zettel, get_zettels, print_zettel


@dataclass
class Config:
    repo_path: Path = const.DEFAULT_REPO_PATH
    editor: Path = const.VIM_WINDOWS_PATH


def main(argv: list[str] | None = None) -> int:
    _configure_console_print_utf8()
    logging.basicConfig(level=logging.INFO)

    parser = _get_parser()
    args = parser.parse_args(argv)

    try:
        return _parse_args(args)
    except NotImplementedError:
        parser.print_usage()
        return 0


def _configure_console_print_utf8() -> None:
    # https://stackoverflow.com/a/60634040/14458327
    if isinstance(sys.stdout, io.TextIOWrapper):
        # if statement is needed to satisfy mypy
        # https://github.com/python/typeshed/issues/3049
        sys.stdout.reconfigure(encoding="utf-8")


def _get_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pyzet", formatter_class=argparse.RawTextHelpFormatter
    )

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {const.VERSION}",
    )

    parser.add_argument("-r", "--repo", help="path to point to any zet repo")

    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser(
        "status",
        help="run `git status` in zet repo,\nuse `--` before including git options",
    )
    status_parser.add_argument(
        "options",
        action="store",
        type=str,
        nargs="*",
        default=[],
        help="`git status` options, use `--` before including them",
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

    show_parser = subparsers.add_parser("show", help="print zettel contents")
    show_parser.add_argument("id", nargs=1, help="zettel id (timestamp)")

    clean_parser = subparsers.add_parser(
        "clean", help="delete empty folders in zet repo"
    )
    clean_parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="list what will be deleted, but don't delete it",
    )

    subparsers.add_parser("add", help="add a new zettel")

    edit_parser = subparsers.add_parser("edit", help="edit a zettel")
    edit_parser.add_argument("id", nargs=1, help="zettel id (timestamp)")

    remove_parser = subparsers.add_parser("rm", help="remove a zettel")
    remove_parser.add_argument("id", nargs=1, help="zettel id (timestamp)")

    push_parser = subparsers.add_parser(
        "push",
        help="run `git push` in zet repo,\nuse `--` before including git options",
    )
    push_parser.add_argument(
        "options",
        action="store",
        type=str,
        nargs="*",
        default=[],
        help="`git status` options, use `--` before including them",
    )

    return parser


def _parse_args(args: Namespace) -> int:
    config = _get_config(args.repo)
    try:
        id_ = args.id[0]
    except AttributeError:
        pass  # command that doesn't use `id` was executed
    else:
        return _parse_args_with_id(id_, args.command, config)
    return _parse_args_without_id(args, config)


def _get_config(args_repo_path: str) -> Config:
    """Gets config values from CLI or from default value and validates them."""
    config = Config()
    if args_repo_path:
        config.repo_path = Path(args_repo_path)
    if not config.repo_path.is_dir():
        raise SystemExit(
            "ERROR: wrong repo path. "
            f"Create folder `{config.repo_path}` or use `--repo` flag."
        )
    return config


def _parse_args_with_id(id_: str, command: str, config: Config) -> int:
    _validate_id(id_, command, config)

    if command == "show":
        return show_zettel(config.repo_path, id_)

    if command == "edit":
        return edit_zettel(id_, config)

    if command == "rm":
        return remove_zettel(config.repo_path, id_)

    raise NotImplementedError


def _parse_args_without_id(args: Namespace, config: Config) -> int:
    if args.command == "add":
        return add_zettel(config)

    if args.command == "list":
        return list_zettels(
            config.repo_path, is_pretty=args.pretty, is_reversed=args.reverse
        )

    if args.command == "tags":
        if args.count:
            return count_tags(config.repo_path)
        return list_tags(config.repo_path, is_reversed=args.reverse)

    if args.command == "status":
        return get_repo_status(config.repo_path, args.options)

    if args.command == "push":
        return push_to_remote(config.repo_path, args.options)

    if args.command == "clean":
        return clean_zet_repo(config.repo_path, is_dry_run=args.dry_run)

    raise NotImplementedError


def _validate_id(id_: str, command: str, config: Config) -> None:
    zettel_dir = Path(config.repo_path, const.ZETDIR, id_)
    if not zettel_dir.is_dir():
        raise SystemExit(f"ERROR: folder {id_} doesn't exist")
    if not Path(zettel_dir, const.ZETTEL_FILENAME).is_file():
        if command == "rm":
            raise SystemExit(
                f"ERROR: {const.ZETTEL_FILENAME} in {id_} doesn't exist. "
                "Use `pyzet clean` to remove empty folder"
            )
        raise SystemExit(f"ERROR: {const.ZETTEL_FILENAME} in {id_} doesn't exist")


def get_repo_status(path: Path, options: list[str]) -> int:
    subprocess.call([_get_git_cmd(), "-C", path, "status", *options])
    return 0


def push_to_remote(path: Path, options: list[str]) -> int:
    subprocess.call([_get_git_cmd(), "-C", path, "push", *options])
    return 0


def list_zettels(path: Path, is_pretty: bool, is_reversed: bool) -> int:
    for zettel in get_zettels(Path(path, const.ZETDIR), is_reversed):
        representation = zettel.timestamp if is_pretty else zettel.id_
        print(f"{representation} - {zettel.title}")
    return 0


def list_tags(path: Path, is_reversed: bool) -> int:
    tags: defaultdict[str, int] = defaultdict(int)
    for zettel in get_zettels(Path(path, const.ZETDIR)):
        for tag in zettel.tags:
            tags[tag] += 1

    # sort by occurrence, and then by the tag name
    # https://stackoverflow.com/a/613230/14458327
    for occurrences, tag in sorted(
        ((value, key) for key, value in tags.items()), reverse=is_reversed
    ):
        print(f"{occurrences}\t#{tag}")

    return 0


def count_tags(path: Path) -> int:
    total_tags = 0
    for zettel in get_zettels(Path(path, const.ZETDIR)):
        total_tags += len(zettel.tags)
    print(total_tags)
    return 0


def show_zettel(repo_path: Path, id_: str) -> int:
    zettel = get_zettel(Path(repo_path, const.ZETDIR, id_))
    print_zettel(zettel)
    return 0


def clean_zet_repo(repo_path: Path, is_dry_run: bool) -> int:
    for item in sorted(Path(repo_path, const.ZETDIR).iterdir(), reverse=True):
        if item.is_dir() and _is_empty(item):
            if is_dry_run:
                print(f"will delete {item.name}")
            else:
                print(f"deleting {item.name}")
                item.rmdir()
    return 0


def _is_empty(folder: Path) -> bool:
    # https://stackoverflow.com/a/54216885/14458327
    return not any(Path(folder).iterdir())


def add_zettel(config: Config) -> int:
    """Adds zettel and commits the changes with zettel title as the commit message."""
    id_ = datetime.utcnow().strftime(const.ZULU_DATETIME_FORMAT)

    zettel_dir = Path(config.repo_path, const.ZETDIR, id_)
    zettel_dir.mkdir(parents=True, exist_ok=True)

    zettel_path = Path(zettel_dir, const.ZETTEL_FILENAME)

    with open(zettel_path, "w+") as file:
        file.write("# ")

    _open_file(zettel_path, config.editor)
    logging.info(f"{id_} was created")

    zettel = get_zettel(zettel_path.parent)
    _commit_zettel(config.repo_path, zettel_path, zettel.title)

    return 0


def edit_zettel(id_: str, config: Config) -> int:
    """Edits zettel and commits the changes with `ED:` in the commit message."""
    zettel_path = Path(config.repo_path, const.ZETDIR, id_, const.ZETTEL_FILENAME)
    _open_file(zettel_path, config.editor)
    logging.info(f"{id_} was edited")

    zettel = get_zettel(zettel_path.parent)
    _commit_zettel(config.repo_path, zettel_path, f"ED: {zettel.title}")

    return 0


def _open_file(filename: Path, editor: Path) -> None:
    if sys.platform == "win32":
        subprocess.call([editor, filename])
    else:
        vim_path = shutil.which("vi")

        if vim_path is None:
            raise SystemExit("ERROR: `vi` cannot be found by `which` command")

        opener = "open" if sys.platform == "darwin" else vim_path
        subprocess.call([opener, filename])


def remove_zettel(repo_path: Path, id_: str) -> int:
    """Removes zettel and commits the changes with `RM:` in the commit message."""
    if input(f"{id_} will be deleted. Are you sure? (y/N): ") != "y":
        raise SystemExit("aborting")
    zettel_path = Path(repo_path, const.ZETDIR, id_, const.ZETTEL_FILENAME)
    zettel = get_zettel(zettel_path.parent)

    zettel_path.unlink()
    logging.info(f"{id_} was removed")
    _commit_zettel(repo_path, zettel_path, f"RM: {zettel.title}")

    # If dir is removed before committing, git raises a warning that dir doesn't exist
    zettel_path.parent.rmdir()

    return 0


def _commit_zettel(repo_path: Path, zettel_path: Path, message: str) -> None:
    git_cmd = _get_git_cmd()
    subprocess.call([git_cmd, "-C", repo_path, "add", zettel_path])
    subprocess.call([git_cmd, "-C", repo_path, "commit", "-m", message])


def _get_git_cmd() -> Path:
    git_path = shutil.which("git")
    if git_path is None:
        raise SystemExit("ERROR: `git` cannot be found by `which` command")
    return Path(git_path)
