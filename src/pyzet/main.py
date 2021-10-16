import argparse
from typing import List, Optional

import pyzet.constants as const
from pyzet.zet import get_zets


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="pyzet")

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {const.VERSION}",
    )

    subparsers = parser.add_subparsers(dest="command")
    list_parser = subparsers.add_parser("list", help="list zets in given repo")
    list_parser.add_argument("path", nargs=1, help="path to zet repo")

    args = parser.parse_args(argv)

    if args.command == "list":
        return list_zets(args.path[0])

    parser.print_usage()

    return 0


def list_zets(path: str) -> int:
    for zet in get_zets(path):
        print(f"{zet.timestamp} - {zet.title}")
    return 0
