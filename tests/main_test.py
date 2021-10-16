import pytest

from pyzet.main import main


def test_overall_help(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])

    out, err = capsys.readouterr()

    assert out.startswith("usage: pyzet")
    assert err == ""
