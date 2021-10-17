import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import toml

import pyzet.constants as const
from pyzet.zet import get_zet, get_zets, print_zet


@dataclass
class Config:
    repo_path: Path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="pyzet")

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {const.VERSION}",
    )

    parser.add_argument(
        "-c",
        "--config",
        default=const.CONFIG_FILE,
        help="path to alternate config file",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list", help="list zets in given repo")

    show_parser = subparsers.add_parser("show", help="print zet contents")
    show_parser.add_argument("timestamp", nargs=1, help="zet timestamp")

    args = parser.parse_args(argv)

    config = parse_config(args.config, is_default=args.config == const.CONFIG_FILE)

    if args.command == "list":
        return list_zets(config.repo_path)

    if args.command == "show":
        return show_zet(config.repo_path, args.timestamp[0])

    parser.print_usage()

    return 0


def list_zets(path: Path) -> int:
    for zet in get_zets(path):
        print(f"{zet.timestamp} - {zet.title}")
    return 0


def show_zet(repo_path: Path, timestamp: str) -> int:
    zet = get_zet(Path(repo_path, timestamp))
    print_zet(zet)
    return 0


def parse_config(config_file: str, is_default: bool) -> Config:
    try:
        config = toml.load(Path(config_file))
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        if is_default:
            return _give_default_config()
        raise SystemExit("ERROR: config file not found on given path")
    except toml.TomlDecodeError:
        raise SystemExit("ERROR: cannot parse the file as TOML")

    return Config(repo_path=Path(Path(config_file).parent, config["repo"]["path"]))


def _give_default_config() -> Config:
    return Config(repo_path=Path("."))
