from pathlib import Path

import pytest

from pyzet.constants import ZETDIR
from pyzet.zettel import (
    Zettel,
    get_markdown_title,
    get_zettel,
    get_zettels,
    print_zettel,
)


def test_get_zettels():
    output = get_zettels(path=Path("testing/zet", ZETDIR))

    assert output == [
        Zettel(
            title="Zet test entry",
            id_="20211016205158",
            text=[
                "# Zet test entry\n",
                "\n",
                "Hello there!\n",
                "\n",
                "Tags:\n",
                "\n",
                "    #test-tag #another-tag  #tag-after-two-spaces\n",
            ],
            tags=["test-tag", "another-tag", "tag-after-two-spaces"],
        ),
        Zettel(
            title="Another zet test entry",
            id_="20211016223643",
            text=["# Another zet test entry\n", "\n", "Hello everyone\n"],
        ),
    ]


def test_get_zettels_reverse():
    output = get_zettels(path=Path("testing/zet", ZETDIR), is_reversed=True)

    assert output == [
        Zettel(
            title="Another zet test entry",
            id_="20211016223643",
            text=["# Another zet test entry\n", "\n", "Hello everyone\n"],
        ),
        Zettel(
            title="Zet test entry",
            id_="20211016205158",
            text=[
                "# Zet test entry\n",
                "\n",
                "Hello there!\n",
                "\n",
                "Tags:\n",
                "\n",
                "    #test-tag #another-tag  #tag-after-two-spaces\n",
            ],
            tags=["test-tag", "another-tag", "tag-after-two-spaces"],
        ),
    ]


def test_open_zettel():
    expected = Zettel(
        title="Zet test entry",
        id_="20211016205158",
        text=[
            "# Zet test entry\n",
            "\n",
            "Hello there!\n",
            "\n",
            "Tags:\n",
            "\n",
            "    #test-tag #another-tag  #tag-after-two-spaces\n",
        ],
        tags=["test-tag", "another-tag", "tag-after-two-spaces"],
    )

    assert get_zettel(Path(f"testing/zet/{ZETDIR}/20211016205158")) == expected


def test_print_zettel(capsys):
    test_zettel = Zettel(
        title="Zet test entry",
        id_="20211016205158",
        text=["# Zet test entry\n", "\n", "Hello there!\n"],
    )

    print_zettel(test_zettel)

    out, err = capsys.readouterr()
    assert out == "# Zet test entry\n\nHello there!\n"
    assert err == ""


def test_get_markdown_title():
    assert get_markdown_title("# Sample title", id_="") == "Sample title"


@pytest.mark.parametrize(
    "test_input",
    [
        "#  Additional space",
        "#   Additional two spaces",
        "## Wrong title level",
        "#Missing space",
        "##Missing space and wrong title level",
        "#",
        "##",
        "",
        "Title without leading #",
        " # Leading space",
        "# Trailing space ",
        " # Leading and trailing space ",
    ],
)
def test_get_markdown_title_warning(test_input, caplog):
    assert get_markdown_title(test_input, id_="20211016205159") == test_input
    assert f'wrong title formatting: 20211016205159 "{test_input}"' in caplog.text
