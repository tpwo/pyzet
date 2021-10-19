import sys
from pathlib import Path

if sys.version_info < (3, 8):  # pragma: no cover (<PY38)
    import importlib_metadata
else:  # pragma: no cover (PY38+)
    import importlib.metadata as importlib_metadata

VERSION = importlib_metadata.version("pyzet")

ZETTEL_FILENAME = "README.md"
ZULU_DATETIME_FORMAT = "%Y%m%d%H%M%S"

# Well formatted Markdown title:
# - single # and a single space between it and the rest of the title
# - no leading or trailing spaces
MARKDOWN_TITLE = r"^#\s([\S]+.*[\S])$"

# Path to vim which is installed with Git for Windows
VIM_WINDOWS_PATH = Path("C:/Program Files/Git/usr/bin/vim.exe")
DEFAULT_REPO_PATH = Path(Path.home(), "zet")
