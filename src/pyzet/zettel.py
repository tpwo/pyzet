from __future__ import annotations

import contextlib
import logging
import os
import re
import subprocess
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING
from typing import NamedTuple

import pyzet.constants as const
from pyzet.config import Config
from pyzet.exceptions import NotEnteredError
from pyzet.exceptions import NotFoundError
from pyzet.grep import parse_grep_patterns
from pyzet.utils import get_git_output

if TYPE_CHECKING:
    from pyzet.cli import AppState
    from pyzet.config import Config


class Zettel(NamedTuple):
    """Represents a single zettel.

    Zettel contents are skipped for performance reasons.
    """

    title: str
    id: str
    tags: tuple[str, ...]
    path: Path


def get_all(path: Path, *, is_reversed: bool = False) -> list[Zettel]:
    """Get all zettels from a given repo."""
    if not path.is_dir():
        raise SystemExit(f"ERROR: folder {path} doesn't exist.")
    items: list[Zettel] = []
    for item in sorted(path.iterdir(), reverse=is_reversed):
        if item.is_dir():
            try:
                items.append(get_from_dir(item))
                logging.debug('get_all: found %s', items[-1])
            except FileNotFoundError:
                logging.warning("empty zet folder '%s' detected", item.name)
            except ValueError:
                # Skips dirs with different naming convention and skips
                # zettels without a text in the first line (i.e. during
                # editing).
                logging.debug("get_zettels: ValueError '%s'", item.absolute())
    if items == []:
        raise SystemExit('ERROR: there are no zettels at given repo.')
    return items


def select_from_grep(args: AppState, config: Config) -> Zettel:
    matches = get_from_grep(args, config)

    num_matches = len(matches)
    confirmation_threshold = 50
    if num_matches > confirmation_threshold:
        prompt = (
            f'Are you sure to continue with {num_matches} matches? (y/N): '
        )
        try:
            if input(prompt) != 'y':
                print('aborting')
                raise NotFoundError
        except KeyboardInterrupt as err:
            print('\naborting')
            raise NotFoundError from err

    zero_padding = len(str(num_matches))
    for idx, zet in matches.items():
        print(f'[{str(idx).zfill(zero_padding)}] {get_repr(zet, args)}')

    if num_matches == 1:
        try:
            if input('Continue? (Y/n): ') != 'n':
                args.id = matches[1].id
                return matches[1]
        except KeyboardInterrupt as err:
            print('\naborting')
            raise NotEnteredError from err
        else:
            print('aborting')
            raise NotEnteredError

    while True:
        try:
            user_input = input('#? ')
            if user_input == '':
                print('aborting')
                raise NotEnteredError
            try:
                idx = int(user_input)
                args.id = matches[idx].id
                return matches[idx]
            except (KeyError, ValueError):
                print('Wrong ID provided!')
        except KeyboardInterrupt as err:
            print('\naborting')
            raise NotEnteredError from err


def get_from_grep(args: AppState, config: Config) -> dict[int, Zettel]:
    if _patterns_empty(args.patterns):
        print('Wrong value provided (empty or whitespace)!')
        raise NotFoundError
    opts = ['-I', '--all-match', '--name-only', '--ignore-case']
    opts.extend(
        [
            *parse_grep_patterns(args.patterns),
            '--',
            f'*/{const.ZETTEL_FILENAME}',
        ]
    )
    try:
        out = get_git_output(config, 'grep', opts).decode()
    except subprocess.CalledProcessError as err:
        print('No zettels found!')
        raise NotFoundError from err

    matches: dict[int, Zettel] = {}
    for idx, filename in enumerate(out.splitlines(), start=1):
        matches[idx] = get(Path(config.repo, filename))
    return matches


def _patterns_empty(patterns: list[str]) -> bool:
    """Return True if all provided patterns are empty str or whitespace."""
    return all(s == '' or s.isspace() for s in patterns)


def get_from_id(id_: str, repo: Path) -> Zettel:
    """Get zettel from its ID given repo path."""
    try:
        return get_from_dir(Path(repo, const.ZETDIR, id_))
    except FileNotFoundError as err:
        raise SystemExit(f"ERROR: zettel '{id_}' doesn't exist.") from err


def get_last(repo: Path) -> Zettel:
    """Get the last zettel from a given repo."""
    return get_all(Path(repo, const.ZETDIR), is_reversed=True)[0]


def get_from_dir(dirpath: Path) -> Zettel:
    """Get zettel from a directory named after its ID."""
    return get(Path(dirpath, const.ZETTEL_FILENAME))


def get(path: Path) -> Zettel:
    """Get zettel from a full path."""
    if path.is_dir():
        raise ValueError

    title_line, tags_line = _get_first_and_last_line(path)
    if title_line == '':
        raise ValueError

    tags = get_tags(tags_line.strip()) if tags_line.startswith(4 * ' ') else ()

    id_ = path.parent.name

    zettel = Zettel(
        id=id_,
        title=get_markdown_title(title_line.strip(), id_),
        path=path,
        tags=tags,
    )
    logging.debug('zettel.get: %s', zettel)
    return zettel


def get_repr(zet: Zettel, args: AppState) -> str:
    tags = ''
    if args.tags:
        with contextlib.suppress(ValueError):
            tags = f'  [{get_tags_str(zet)}]'
    if args.pretty:
        return f'{get_timestamp(zet.id)} -- {zet.title}{tags}'
    try:
        if args.link:
            return get_md_link(zet)
    except AttributeError:  # 'Namespace' object has no attribute 'link'
        pass
    return f'{zet.id} -- {zet.title}{tags}'


def get_timestamp(id_: str) -> str:
    """Parse zettel ID into a `YYYY-MM-DD HH:MM:SS` str."""
    return (
        datetime.strptime(id_, const.ZULU_DATETIME_FORMAT)
        .replace(tzinfo=timezone.utc)
        .strftime(const.PRETTY_DATETIME_FORMAT)
    )


def get_md_link(zet: Zettel) -> str:
    """Return a representation of a zettel that is a relative Markdown link.

    Asterisk at the beginning is a Markdown syntax for an unordered list,
    as links to zettels are usually just used in references section of a
    zettel.
    """
    return f'* [{zet.id}](../{zet.id}) {zet.title}'


def get_markdown_title(title_line: str, id_: str) -> str:
    """Extract Markdown title if it is formatted correctly.

    Otherwise, returns the whole line and logs a warning. 'title_line'
    arg should have newline characters stripped.

    Raises ValueError if empty or whitespace only title is given as
    input.
    """
    if title_line == '':
        raise ValueError('Empty zettel title found')
    result = re.match(const.MARKDOWN_TITLE, title_line)
    if not result:
        logging.warning('wrong title formatting: %s "%s"', id_, title_line)
        return title_line
    res = result.groups()[0]
    logging.debug("get_markdown_title: '%s' -> '%s'", title_line, res)
    return res


def get_tags(line: str) -> tuple[str, ...]:
    """Parse tags from a line of text."""
    tags = tuple(sorted(tag.lstrip('#') for tag in line.split()))
    logging.debug('get_tags: got %s', tags)
    return tags


def get_tags_str(zettel: Zettel) -> str:
    """Parse zettel tags into a printable repr."""
    if zettel.tags == ():
        raise ValueError
    else:
        return '#' + ' #'.join(zettel.tags)


def _get_first_and_last_line(path: Path) -> tuple[str, str]:
    """Get the first and the last line from a given file.

    It uses file.seek() to look from the end of the file. It's fast but
    requires the file to be opened in binary mode.

    Reference:
    https://stackoverflow.com/a/54278929/14458327
    """
    with open(path, 'rb') as file:
        title_line = file.readline().decode('utf-8')
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:  # file has only a single line
            file.seek(0)
        tags_line = file.readline().decode('utf-8')
    return title_line, tags_line
