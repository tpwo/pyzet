import pyzet.constants as C

SAMPLE_CONFIG = f"""\
# See https://github.com/wojdatto/pyzet.git for more information.
#
# Put this file at {C.DEFAULT_CFG_LOCATION.as_posix()}
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: /usr/bin/vim
git: /usr/bin/git
"""


def sample_config() -> int:
    print(SAMPLE_CONFIG, end="")
    return 0
