from datetime import datetime
from pathlib import Path

import pytest

from pyzet.zet import Zet, get_markdown_title, get_zet, get_zets, print_zet


def test_get_zets():
    output = get_zets(path=Path("tests/files/zet"))

    assert output == [
        Zet(
            title="Zet test entry",
            timestamp=datetime(2021, 10, 16, 20, 51, 58),
            text=["# Zet test entry\n", "\n", "Hello there!\n"],
        ),
        Zet(
            title="Another zet test entry",
            timestamp=datetime(2021, 10, 16, 22, 36, 43),
            text=["# Another zet test entry\n", "\n", "Hello everyone\n"],
        ),
    ]


def test_open_zet():
    expected = Zet(
        title="Zet test entry",
        timestamp=datetime(2021, 10, 16, 20, 51, 58),
        text=["# Zet test entry\n", "\n", "Hello there!\n"],
    )

    assert get_zet(Path("tests/files/zet/20211016205158")) == expected


def test_print_zet(capsys):
    test_zet = Zet(
        title="Zet test entry",
        timestamp=datetime(2021, 10, 16, 20, 51, 58),
        text=["# Zet test entry\n", "\n", "Hello there!\n"],
    )

    print_zet(test_zet)

    out, err = capsys.readouterr()
    assert out == "# Zet test entry\n\nHello there!\n"
    assert err == ""


def test_get_markdown_title():
    assert get_markdown_title("# Sample title", zet_name="") == "Sample title"


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
    timestamp = "20211016205159"
    assert get_markdown_title(test_input, zet_name=timestamp) == test_input
    assert f"wrong title formatting: {timestamp} {test_input}" in caplog.text
