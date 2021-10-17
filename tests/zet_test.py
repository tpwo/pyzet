from pathlib import Path

import pytest

from pyzet.zet import Zet, get_markdown_title, get_zet, get_zets, print_zet


def test_get_zets():
    output = get_zets(path=Path("tests/files/zet"))

    assert output == [
        Zet(
            title="Zet test entry",
            id_="20211016205158",
            text=["# Zet test entry\n", "\n", "Hello there!\n"],
        ),
        Zet(
            title="Another zet test entry",
            id_="20211016223643",
            text=["# Another zet test entry\n", "\n", "Hello everyone\n"],
        ),
    ]


def test_open_zet():
    expected = Zet(
        title="Zet test entry",
        id_="20211016205158",
        text=["# Zet test entry\n", "\n", "Hello there!\n"],
    )

    assert get_zet(Path("tests/files/zet/20211016205158")) == expected


def test_print_zet(capsys):
    test_zet = Zet(
        title="Zet test entry",
        id_="20211016205158",
        text=["# Zet test entry\n", "\n", "Hello there!\n"],
    )

    print_zet(test_zet)

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
    id_ = "20211016205159"
    assert get_markdown_title(test_input, id_=id_) == test_input
    assert f"wrong title formatting: {id_} {test_input}" in caplog.text