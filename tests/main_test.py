import pytest

from pyzet.main import main


def test_main(capsys):
    with pytest.raises(SystemExit):
        main(["-h"])

    out, err = capsys.readouterr()

    assert out.startswith("usage: pyzet")
    assert err == ""
