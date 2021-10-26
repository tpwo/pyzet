import argparse
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pyzet.constants as const
from pyzet.zettel import get_zettel, get_zettels, print_zettel


@dataclass
class Config:
    repo_path: Path = const.DEFAULT_REPO_PATH
    editor: Path = const.VIM_WINDOWS_PATH


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(prog="pyzet")

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
        help="run `git status` in zet repo, use `--` before including git options",
    )
    status_parser.add_argument(
        "options",
        action="store",
        type=str,
        nargs="*",
        default=["."],
        help="`git status` options, use `--` before including them",
    )

    list_parser = subparsers.add_parser("list", help="list zettels in given repo")
    list_parser.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="use prettier format for printing date and time",
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

    args = parser.parse_args(argv)

    config = Config()

    if args.repo:
        config.repo_path = Path(args.repo)

    if not config.repo_path.is_dir():
        raise SystemExit(
            "ERROR: wrong repo path. "
            f"Create folder `{config.repo_path}` or use `--repo` flag."
        )

    try:
        if args.id:
            _validate_id(args, config)
    except AttributeError:
        pass  # command that doesn't use `id` was executed

    if args.command == "status":
        return get_repo_status(config.repo_path, args.options)

    if args.command == "list":
        return list_zets(config.repo_path, is_pretty=args.pretty)

    if args.command == "show":
        return show_zet(config.repo_path, args.id[0])

    if args.command == "clean":
        return clean_zet_repo(config.repo_path, is_dry_run=args.dry_run)

    if args.command == "add":
        return add_zettel(config)

    if args.command == "edit":
        return edit_zettel(args.id[0], config)

    if args.command == "rm":
        return remove_zettel(config.repo_path, args.id[0])

    parser.print_usage()

    return 0


def _validate_id(args: argparse.Namespace, config: Config) -> None:
    zettel_dir = Path(config.repo_path, const.ZETDIR, args.id[0])
    if not zettel_dir.is_dir():
        raise SystemExit(f"ERROR: folder {args.id[0]} doesn't exist")
    if not Path(zettel_dir, const.ZETTEL_FILENAME).is_file():
        if args.command == "rm":
            raise SystemExit(
                f"ERROR: {const.ZETTEL_FILENAME} in {args.id[0]} doesn't exist. "
                "Use `pyzet clean` to remove empty folder"
            )
        raise SystemExit(
            f"ERROR: {const.ZETTEL_FILENAME} in {args.id[0]} doesn't exist"
        )


def get_repo_status(path: Path, options: List[str]) -> int:
    subprocess.call([_get_git_cmd(), "-C", path, "status", *options])
    return 0


def list_zets(path: Path, is_pretty: bool) -> int:
    for zettel in get_zettels(Path(path, const.ZETDIR)):
        representation = zettel.timestamp if is_pretty else zettel.id_
        print(f"{representation} - {zettel.title}")
    return 0


def show_zet(repo_path: Path, id_: str) -> int:
    zettel = get_zettel(Path(repo_path, const.ZETDIR, id_))
    print_zettel(zettel)
    return 0


def clean_zet_repo(repo_path: Path, is_dry_run: bool) -> int:
    for item in Path(repo_path, const.ZETDIR).iterdir():
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
    if input(f"{id_} will be deleted. Are you sure? (y/N): ") != "y":
        raise SystemExit("aborting")
    zettel_path = Path(repo_path, const.ZETDIR, id_, const.ZETTEL_FILENAME)
    zettel_path.unlink()
    zettel_path.parent.rmdir()
    logging.info(f"{id_} was removed")
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
