import argparse
import logging
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pyzet.constants as const
from pyzet.zet import get_zet, get_zets, print_zet


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

    list_parser = subparsers.add_parser("list", help="list zets in given repo")
    list_parser.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="use prettier format for printing date and time",
    )

    show_parser = subparsers.add_parser("show", help="print zet contents")
    show_parser.add_argument("id", nargs=1, help="zet id (timestamp)")

    clean_parser = subparsers.add_parser(
        "clean", help="delete empty folders in zet repo"
    )
    clean_parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="list what will be deleted, but don't delete it",
    )

    subparsers.add_parser("add", help="add a new zet")

    edit_parser = subparsers.add_parser("edit", help="edit a zet")
    edit_parser.add_argument("id", nargs=1, help="zet id (timestamp)")

    remove_parser = subparsers.add_parser("rm", help="remove a zet")
    remove_parser.add_argument("id", nargs=1, help="zet id (timestamp)")

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

    if args.command == "list":
        return list_zets(config.repo_path, is_pretty=args.pretty)

    if args.command == "show":
        return show_zet(config.repo_path, args.id[0])

    if args.command == "clean":
        return clean_zets(config.repo_path, is_dry_run=args.dry_run)

    if args.command == "add":
        return add_zet(config)

    if args.command == "edit":
        return edit_zet(args.id[0], config)

    if args.command == "rm":
        return remove_zet(config.repo_path, args.id[0])

    parser.print_usage()

    return 0


def _validate_id(args: argparse.Namespace, config: Config) -> None:
    if not Path(config.repo_path, args.id[0]).is_dir():
        raise SystemExit(f"ERROR: folder {args.id[0]} doesn't exist")
    if not Path(config.repo_path, args.id[0], const.ZET_FILENAME).is_file():
        if args.command == "rm":
            raise SystemExit(
                f"ERROR: {const.ZET_FILENAME} in {args.id[0]} doesn't exist. "
                "Use `pyzet clean` to remove empty folder"
            )
        raise SystemExit(f"ERROR: {const.ZET_FILENAME} in {args.id[0]} doesn't exist")


def list_zets(path: Path, is_pretty: bool) -> int:
    for zet in get_zets(path):
        representation = zet.timestamp if is_pretty else zet.id_
        print(f"{representation} - {zet.title}")
    return 0


def show_zet(repo_path: Path, id_: str) -> int:
    zet = get_zet(Path(repo_path, id_))
    print_zet(zet)
    return 0


def clean_zets(repo_path: Path, is_dry_run: bool) -> int:
    for item in repo_path.iterdir():
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


def add_zet(config: Config) -> int:
    id_ = datetime.utcnow().strftime(const.ZULU_DATETIME_FORMAT)
    Path(config.repo_path, id_).mkdir(parents=True, exist_ok=True)

    zet_file_path = Path(config.repo_path, id_, const.ZET_FILENAME)

    with open(zet_file_path, "w+") as file:
        file.write("# ")

    _open_file(zet_file_path, config.editor)
    logging.info(f"{id_} was created")
    return 0


def edit_zet(id_: str, config: Config) -> int:
    _open_file(Path(config.repo_path, id_, const.ZET_FILENAME), config.editor)
    logging.info(f"{id_} was edited")
    return 0


def _open_file(filename: Path, editor: Path) -> None:
    if sys.platform == "win32":
        subprocess.call([editor, filename], shell=True)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def remove_zet(repo_path: Path, id_: str) -> int:
    if input(f"{id_} will be deleted. Are you sure? (y/N): ") != "y":
        raise SystemExit("aborting")
    Path(repo_path, id_, const.ZET_FILENAME).unlink()
    Path(repo_path, id_).rmdir()
    logging.info(f"{id_} was removed")
    return 0
