from __future__ import annotations

import sys
from importlib import metadata
from pathlib import Path

VERSION = metadata.version('pyzet')

CONFIG_FILE = 'pyzet.yaml'
DEFAULT_CFG_LOCATION = Path(Path.home(), '.config', 'pyzet', CONFIG_FILE)

DEFAULT_BRANCH = 'main'
DEFAULT_REMOTE_NAME = 'origin'

ZETDIR = 'docs'
ZETTEL_FILENAME = 'README.md'

ZULU_DATETIME_FORMAT = '%Y%m%d%H%M%S'
ZULU_FORMAT_LEN = 14

ZETTEL_WIDTH = 72

# Well formatted Markdown title:
# - single # and a single space between it and the rest of the title
# - no leading or trailing spaces
MARKDOWN_TITLE = r'^#\s(\S.*\S)$'

vim_win_path = Path('C:/Program Files/Git/usr/bin/vim.exe').as_posix()
vim_unix_path = Path('/usr/bin/vim').as_posix()
VIM_PATH = vim_win_path if sys.platform == 'win32' else vim_unix_path
