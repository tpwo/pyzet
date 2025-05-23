"""Logic for parsing pyzet config file."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING
from typing import NamedTuple

import yaml

import pyzet.constants as const

if TYPE_CHECKING:
    from pyzet.cli import AppState


class Config(NamedTuple):
    """Pyzet config representation."""

    repo: Path
    editor: str
    editor_args: tuple[str, ...]


def get(args: AppState) -> Config:
    """Get config from YAML."""
    try:
        with open(args.config) as file:
            yaml_cfg = yaml.safe_load(file)
    except FileNotFoundError as err:
        raise SystemExit(
            f"ERROR: config file at '{Path(args.config).as_posix()}' "
            "not found.\nAdd it or use '--config' flag."
        ) from err
    config = _process_yaml(yaml_cfg, args.config, args.repo)
    # if we initialize repo, the folder may not exist
    if args.command == 'init':
        if args.path:
            return config._replace(repo=Path(args.path))
        return config
    if not config.repo.is_dir():
        raise SystemExit(
            'ERROR: wrong repo path. '
            "Run 'pyzet init' to create a git repo at "
            f"'{config.repo}', or use '--repo' flag."
        )
    return config


def _process_yaml(
    yaml_cfg: dict[str, object], config_file: str, repo_path: str | None = None
) -> Config:
    """Process YAML config file.

    Only 'repo' field is required. If other fields are missing,
    a default value will be used.
    """
    if repo_path:
        repo = Path(repo_path)
    else:
        try:
            repo_raw = yaml_cfg['repo']
            assert isinstance(repo_raw, str)
            repo = Path(repo_raw).expanduser()
        except KeyError as err:
            raise SystemExit(
                "ERROR: field 'repo' missing from"
                f" '{Path(config_file).as_posix()}'."
            ) from err

    editor = yaml_cfg.get('editor', const.VIM_PATH)
    assert isinstance(editor, str)

    editor_args = yaml_cfg.get('editor_args', [])
    assert isinstance(editor_args, Iterable)

    return Config(
        repo=repo,
        editor=editor,
        editor_args=tuple(editor_args),
    )
