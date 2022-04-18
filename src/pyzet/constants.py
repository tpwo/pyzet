import sys
from pathlib import Path

if sys.version_info < (3, 8):  # pragma: no cover (<PY38)
    import importlib_metadata
else:  # pragma: no cover (PY38+)
    import importlib.metadata as importlib_metadata

VERSION = importlib_metadata.version("pyzet")

CONFIG_FILE = "pyzet.yaml"
DEFAULT_CFG_LOCATION = Path(Path.home(), ".config", "pyzet", CONFIG_FILE)

ZETDIR = "zettels"
ZETTEL_FILENAME = "README.md"
ZULU_DATETIME_FORMAT = "%Y%m%d%H%M%S"

ZETTEL_WIDTH = 72

# Well formatted Markdown title:
# - single # and a single space between it and the rest of the title
# - no leading or trailing spaces
MARKDOWN_TITLE = r"^#\s([\S]+.*[\S])$"

# Default paths to Unix utilities installed with Git for Windows.
vim_win_path = Path("C:/Program Files/Git/usr/bin/vim.exe").as_posix()
git_win_path = Path("C:/Program Files/Git/cmd/git.exe").as_posix()

# Default paths on Linux (at least on Ubuntu).
vim_unix_path = Path("/usr/bin/vim").as_posix()
git_unix_path = Path("/usr/bin/git").as_posix()

VIM_PATH = vim_win_path if sys.platform == "win32" else vim_unix_path
GIT_PATH = git_win_path if sys.platform == "win32" else git_unix_path
