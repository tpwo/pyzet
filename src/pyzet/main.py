import argparse
from typing import List, Optional

import pyzet.constants as C


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="pyzet")

    # https://stackoverflow.com/a/8521644/812183
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {C.VERSION}",
    )

    parser.parse_args(argv)
    return 0
