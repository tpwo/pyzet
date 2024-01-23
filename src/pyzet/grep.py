from __future__ import annotations

from pathlib import Path

import pyzet.constants as C
from pyzet.cli import AppState
from pyzet.config import Config
from pyzet.utils import call_git


def grep(args: AppState, config: Config) -> None:
    grep_opts = _build_grep_options(
        args.ignore_case, args.line_number, args.title
    )
    patterns = parse_grep_patterns(args.patterns)
    grep_opts.extend(patterns)
    call_git(
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
