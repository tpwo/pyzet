from pathlib import Path

import pytest

import pyzet.constants as C
from pyzet.zettel import get_markdown_title
from pyzet.zettel import get_zettel
from pyzet.zettel import get_zettels
from pyzet.zettel import Zettel


def test_get_zettels():
    output = get_zettels(path=Path("testing/zet", C.ZETDIR))

    assert output == [
        Zettel(
            title="Zet test entry",
            id_="20211016205158",
            tags=["test-tag", "another-tag", "tag-after-two-spaces"],
        ),
        Zettel(
            title="Another zet test entry",
            id_="20211016223643",
            tags=["test-tag"],
        ),
        Zettel(
            title="Zettel with UTF-8",
            id_="20220101220852",
            tags=[],
        ),
    ]


def test_get_zettels_reverse():
    output = get_zettels(path=Path("testing/zet", C.ZETDIR), is_reversed=True)

    assert output == [
        Zettel(
            title="Zettel with UTF-8",
            id_="20220101220852",
            tags=[],
        ),
        Zettel(
            title="Another zet test entry",
            id_="20211016223643",
            tags=["test-tag"],
        ),
        Zettel(
            title="Zet test entry",
            id_="20211016205158",
            tags=["test-tag", "another-tag", "tag-after-two-spaces"],
        ),
    ]


def test_open_zettel():
    expected = Zettel(
        title="Zet test entry",
        id_="20211016205158",
        tags=["test-tag", "another-tag", "tag-after-two-spaces"],
    )

    assert get_zettel(Path(f"testing/zet/{C.ZETDIR}/20211016205158")) == expected


def test_get_markdown_title():
    assert get_markdown_title("# Sample title", id_="") == "Sample title"


@pytest.mark.parametrize(
    "test_input",
    (
        "#  Additional space",
        "#   Additional two spaces",
        "## Wrong title level",
        "#Missing space",
        "##Missing space and wrong title level",
        "#",
        "##",
        "Title without leading #",
        " # Leading space",
        "# Trailing space ",
        " # Leading and trailing space ",
    ),
)
def test_get_markdown_title_warning(test_input, caplog):
    assert get_markdown_title(test_input, id_="20211016205159") == test_input
    assert f'wrong title formatting: 20211016205159 "{test_input}"' in caplog.text


def test_get_markdown_value_error():
    with pytest.raises(ValueError):
        get_markdown_title("", id_="20211016205159")
