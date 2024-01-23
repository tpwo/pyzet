from __future__ import annotations

import pyzet.constants as C


_header = f"""\
# See https://github.com/tpwo/pyzet for more information.
#
# Put this file at {C.DEFAULT_CFG_LOCATION}
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH."""

SAMPLE_CONFIG_UNIX = f"""\
{_header}
repo: ~/zet
editor: {C.vim_unix_path}
editor_args: []
"""

SAMPLE_CONFIG_WINDOWS = f"""\
{_header}
repo: ~/zet
editor: {C.vim_win_path}
editor_args: []
"""


def sample_config(kind: str) -> None:
    if kind == 'unix':
        print(SAMPLE_CONFIG_UNIX, end='')
    elif kind == 'windows':
        print(SAMPLE_CONFIG_WINDOWS, end='')
    else:
        raise NotImplementedError(
            f"ERROR: sample config kind '{kind}' not recognized."
        )
