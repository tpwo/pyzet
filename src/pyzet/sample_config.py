from __future__ import annotations

from typing import TYPE_CHECKING

import pyzet.constants as const

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from argparse import _SubParsersAction


def define_sample_config_cli(
    subparsers: _SubParsersAction[ArgumentParser],
) -> None:
    sample_config_parser = subparsers.add_parser(
        'sample-config', help=f'produce a sample {const.CONFIG_FILE} file'
    )
    sample_config_parser.add_argument('kind', choices=('unix', 'windows'))


_header = f"""\
# See https://github.com/tpwo/pyzet for more information.
#
# Put this file at {const.DEFAULT_CFG_LOCATION.as_posix()}
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH."""

SAMPLE_CONFIG_UNIX = f"""\
{_header}
repo: ~/zet
editor: {const.vim_unix_path}
editor_args: []
"""

SAMPLE_CONFIG_WINDOWS = f"""\
{_header}
repo: ~/zet
editor: {const.vim_win_path}
editor_args: []
"""


def sample_config(kind: str) -> int:
    if kind == 'unix':
        print(SAMPLE_CONFIG_UNIX, end='')
    elif kind == 'windows':
        print(SAMPLE_CONFIG_WINDOWS, end='')
    else:
        raise NotImplementedError(
            f"ERROR: sample config kind '{kind}' not recognized."
        )
    return 0
