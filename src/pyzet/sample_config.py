import pyzet.constants as C

SAMPLE_CONFIG_UNIX = f"""\
# See https://github.com/wojdatto/pyzet for more information.
#
# Put this file at {C.DEFAULT_CFG_LOCATION.as_posix()}
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: {C.vim_unix_path}
git: {C.git_unix_path}
"""

SAMPLE_CONFIG_WINDOWS = f"""\
# See https://github.com/wojdatto/pyzet for more information.
#
# Put this file at {C.DEFAULT_CFG_LOCATION.as_posix()}
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: {C.vim_win_path}
git: {C.git_win_path}
"""


def sample_config(kind: str) -> int:
    if kind == "unix":
        print(SAMPLE_CONFIG_UNIX, end="")
    elif kind == "windows":
        print(SAMPLE_CONFIG_WINDOWS, end="")
    else:
        raise NotImplementedError(f"ERROR: sample config kind '{kind}' not recognized.")
    return 0
