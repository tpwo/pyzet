from datetime import datetime
from pathlib import Path

from pyzet.zet import Zet, get_zet, get_zets


def test_get_zets():
    output = get_zets(path=Path("tests/files/zet"))

    assert output == [
        Zet(title="Zet test entry", timestamp=datetime(2021, 10, 16, 20, 51, 58)),
        Zet(
            title="Another zet test entry", timestamp=datetime(2021, 10, 16, 22, 36, 43)
        ),
    ]


def test_open_zet():
    timestamp = datetime(2021, 10, 16, 20, 51, 58)
    expected = Zet(title="Zet test entry", timestamp=timestamp)

    assert get_zet(Path("tests/files/zet/20211016205158")) == expected
