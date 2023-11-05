from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import pyzet.constants as C
from pyzet.zettel import get_markdown_title
from pyzet.zettel import get_zettel
from pyzet.zettel import get_zettels
from pyzet.zettel import Zettel


def test_get_zettels():
    actual = get_zettels(path=Path('testing/zet', C.ZETDIR))
    expected = [
        Zettel(
            title='Zet test entry',
            id_='20211016205158',
            tags=('another-tag', 'tag-after-two-spaces', 'test-tag'),
            path=Path('testing/zet/zettels/20211016205158/README.md'),
        ),
        Zettel(
            title='Another zet test entry',
            id_='20211016223643',
            tags=('test-tag',),
            path=Path('testing/zet/zettels/20211016223643/README.md'),
        ),
        Zettel(
            title='Zettel with UTF-8',
            id_='20220101220852',
            tags=(),
            path=Path('testing/zet/zettels/20220101220852/README.md'),
        ),
    ]
    assert actual == expected


def test_get_zettels_reverse():
    actual = get_zettels(path=Path('testing/zet', C.ZETDIR), is_reversed=True)
    expected = [
        Zettel(
            title='Zettel with UTF-8',
            id_='20220101220852',
            tags=(),
            path=Path('testing/zet/zettels/20220101220852/README.md'),
        ),
        Zettel(
            title='Another zet test entry',
            id_='20211016223643',
            tags=('test-tag',),
            path=Path('testing/zet/zettels/20211016223643/README.md'),
        ),
        Zettel(
            title='Zet test entry',
            id_='20211016205158',
            tags=('another-tag', 'tag-after-two-spaces', 'test-tag'),
            path=Path('testing/zet/zettels/20211016205158/README.md'),
        ),
    ]
    assert actual == expected


def test_get_zettels_skip_file(tmp_path):
    zettel = 'testing/zet/zettels/20220101220852'
    zet_repo = Path(tmp_path, C.ZETDIR)
    zet_repo.mkdir()
    shutil.copytree(zettel, Path(zet_repo, '20220101220852'))

    # Create a file, to see if it will be correctly skipped
    Path(zet_repo, 'foo').touch()

    actual = get_zettels(zet_repo)
    expected = [
        Zettel(
            title='Zettel with UTF-8',
            id_='20220101220852',
            tags=(),
            path=Path(tmp_path, 'zettels/20220101220852/README.md'),
        )
    ]
    assert actual == expected


def test_get_zettels_dir_not_found():
    with pytest.raises(SystemExit) as excinfo:
        get_zettels(Path('fooBarNonexistent'))
    (msg,) = excinfo.value.args
    assert msg == "ERROR: folder fooBarNonexistent doesn't exist."


def test_open_zettel():
    expected = Zettel(
        title='Zet test entry',
        id_='20211016205158',
        tags=('another-tag', 'tag-after-two-spaces', 'test-tag'),
        path=Path('testing/zet/zettels/20211016205158/README.md'),
    )
    actual = get_zettel(Path(f'testing/zet/{C.ZETDIR}/20211016205158'))
    assert actual == expected


def test_get_markdown_title():
    assert get_markdown_title('# Sample title', id_='') == 'Sample title'


@pytest.mark.parametrize(
    'test_input',
    (
        '#  Additional space',
        '#   Additional two spaces',
        '## Wrong title level',
        '#Missing space',
        '##Missing space and wrong title level',
        '#',
        '##',
        'Title without leading #',
        ' # Leading space',
        '# Trailing space ',
        ' # Leading and trailing space ',
    ),
)
def test_get_markdown_title_warning(test_input, caplog):
    assert get_markdown_title(test_input, id_='20211016205159') == test_input
    msg = f'wrong title formatting: 20211016205159 "{test_input}"'
    assert msg in caplog.text


def test_get_markdown_value_error():
    with pytest.raises(ValueError):
        get_markdown_title('', id_='20211016205159')
