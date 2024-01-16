from __future__ import annotations

from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace
from pathlib import Path

import pyzet.constants as C
from pyzet.config import Config
from pyzet.utils import call_git


def define_grep_cli(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    grep_parser = subparsers.add_parser(
        'grep', help="run 'git grep' with some handy flags in ZK repo"
    )
    grep_parser.add_argument(
        '-i',
        '--ignore-case',
        action='store_true',
        help='case insensitive matching',
    )
    grep_parser.add_argument(
        '-t',
        '--title',
        action='store_true',
        help='add zettel title to matching lines',
    )
    grep_parser.add_argument(
        '-n',
        '--line-number',
        action='store_true',
        help='prefix the line number to matching lines',
    )
    grep_parser.add_argument(
        'patterns',
        nargs='+',
        help="grep patterns, pass 'git grep' options after '--'",
    )


def grep(args: Namespace, config: Config) -> int:
    grep_opts = _build_grep_options(
        args.ignore_case, args.line_number, args.title
    )
    patterns = parse_grep_patterns(args.patterns)
    grep_opts.extend(patterns)
    return call_git(
        config,
        'grep',
        tuple(grep_opts),
        path=Path(config.repo, C.ZETDIR),
    )


def _build_grep_options(
    ignore_case: bool, line_number: bool, title: bool
) -> list[str]:
    opts = ['-I', '--heading', '--break', '--all-match']
    if ignore_case:
        opts.append('--ignore-case')
    if line_number:
        opts.append('--line-number')
    if title:
        zettel_title_pattern = r'^#\s.*'
        opts.extend(_add_git_grep_pattern(zettel_title_pattern))
    return opts


def parse_grep_patterns(patterns: list[str]) -> list[str]:
    opts = []
    for idx, pat in enumerate(patterns):
        if pat.startswith('-'):
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
    return '--or', '-e', pattern
