from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import pyzet.constants as const
from pyzet import zettel
from pyzet.zettel import Zettel
from pyzet.zettel import get_all
from pyzet.zettel import get_markdown_title


def test_get_all():
    actual = get_all(path=Path('testing/zet', const.ZETDIR))
    expected = [
        Zettel(
            title='Zet test entry',
            id='20211016205158',
            tags=('another-tag', 'tag-after-two-spaces', 'test-tag'),
            path=Path('testing/zet/docs/20211016205158/README.md'),
        ),
        Zettel(
            title='Another zet test entry',
            id='20211016223643',
            tags=('test-tag',),
            path=Path('testing/zet/docs/20211016223643/README.md'),
        ),
        Zettel(
            title='Zettel with UTF-8',
            id='20220101220852',
            tags=(),
            path=Path('testing/zet/docs/20220101220852/README.md'),
        ),
    ]
    assert actual == expected


def test_get_all_reverse():
    actual = get_all(path=Path('testing/zet', const.ZETDIR), is_reversed=True)
    expected = [
        Zettel(
            title='Zettel with UTF-8',
            id='20220101220852',
            tags=(),
            path=Path('testing/zet/docs/20220101220852/README.md'),
        ),
        Zettel(
            title='Another zet test entry',
            id='20211016223643',
            tags=('test-tag',),
            path=Path('testing/zet/docs/20211016223643/README.md'),
        ),
        Zettel(
            title='Zet test entry',
            id='20211016205158',
            tags=('another-tag', 'tag-after-two-spaces', 'test-tag'),
            path=Path('testing/zet/docs/20211016205158/README.md'),
        ),
    ]
    assert actual == expected


def test_get_all_skip_file(tmp_path):
    zettel = 'testing/zet/docs/20220101220852'
    zet_repo = Path(tmp_path, const.ZETDIR)
    zet_repo.mkdir()
    shutil.copytree(zettel, Path(zet_repo, '20220101220852'))

    # Create a file, to see if it will be correctly skipped
    Path(zet_repo, 'foo').touch()

    actual = get_all(zet_repo)
    expected = [
        Zettel(
            title='Zettel with UTF-8',
            id='20220101220852',
            tags=(),
            path=Path(tmp_path, 'docs/20220101220852/README.md'),
        )
    ]
    assert actual == expected


def test_get_all_dir_not_found():
    with pytest.raises(SystemExit) as excinfo:
        get_all(Path('fooBarNonexistent'))
    (msg,) = excinfo.value.args
    assert msg == "ERROR: folder fooBarNonexistent doesn't exist."


def test_get():
    expected = Zettel(
        title='Zet test entry',
        id='20211016205158',
        tags=('another-tag', 'tag-after-two-spaces', 'test-tag'),
        path=Path('testing/zet/docs/20211016205158/README.md'),
    )
    dir_ = Path(
        f'testing/zet/{const.ZETDIR}/20211016205158/{const.ZETTEL_FILENAME}'
    )
    actual = zettel.get(dir_)
    assert actual == expected


def test_get_from_dir():
    expected = Zettel(
        title='Zet test entry',
        id='20211016205158',
        tags=('another-tag', 'tag-after-two-spaces', 'test-tag'),
        path=Path('testing/zet/docs/20211016205158/README.md'),
    )
    dir_ = Path(f'testing/zet/{const.ZETDIR}/20211016205158')
    actual = zettel.get_from_dir(dir_)
    assert actual == expected


def test_get_from_id():
    expected = Zettel(
        title='Zet test entry',
        id='20211016205158',
        tags=('another-tag', 'tag-after-two-spaces', 'test-tag'),
        path=Path('testing/zet/docs/20211016205158/README.md'),
    )
    actual = zettel.get_from_id('20211016205158', repo=Path('testing/zet'))
    assert actual == expected


def test_get_last():
    expected = Zettel(
        title='Zettel with UTF-8',
        id='20220101220852',
        tags=(),
        path=Path('testing/zet/docs/20220101220852/README.md'),
    )
    actual = zettel.get_last(Path('testing/zet'))
    assert actual == expected


def test_get_markdown_title():
    assert get_markdown_title('# Sample title', id_='') == 'Sample title'


@pytest.mark.parametrize(
    'test_input',
    [
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
    ],
)
def test_get_markdown_title_warning(test_input, caplog):
    assert get_markdown_title(test_input, id_='20211016205159') == test_input
    msg = f'wrong title formatting: 20211016205159 "{test_input}"'
    assert msg in caplog.text


def test_get_markdown_value_error():
    with pytest.raises(ValueError, match='Empty zettel title found'):
        get_markdown_title('', id_='20211016205159')
