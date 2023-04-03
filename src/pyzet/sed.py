from __future__ import annotations

import logging
import subprocess
from argparse import _SubParsersAction
from argparse import ArgumentParser
from argparse import Namespace

from pyzet.utils import _get_git_bin
from pyzet.utils import Config


def define_sed_cli(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    sed_parser = subparsers.add_parser('sed', help="run 'git sed' in ZK repo")
    sed_parser.add_argument(
        'patterns',
        nargs='+',
        help="sed patterns, pass options after '--'",
    )


def sed(args: Namespace, config: Config) -> int:
    path = config.repo.as_posix()
    ls_files_cmd = (_get_git_bin(), '-C', path, 'ls-files', '-z')
    logging.debug(f'git ls-files: subprocess.run({ls_files_cmd})')
    ls_files = subprocess.run(ls_files_cmd, stdout=subprocess.PIPE)

    opts = _parse_sed_opts(args.patterns)
    xargs_cmd = ('xargs', '-0', 'sed', '-i', *opts)
    logging.debug(f'xargs: subprocess.run({xargs_cmd})')
    subprocess.run(xargs_cmd, input=ls_files.stdout, cwd=path)
    return 0


def _parse_sed_opts(opts: list[str]) -> list[str]:
    out = []
    for idx, pat in enumerate(opts):
        if pat.startswith('-'):
            # Flags started appearing, so there is no more patterns
            out.extend(opts[idx:])
            break
        out.extend(('-e', 'pat'))
    return out
