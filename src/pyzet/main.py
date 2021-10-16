import argparse
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="pyzet")
    parser.parse_args(argv)
    return 0
