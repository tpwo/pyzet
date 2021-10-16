import pytest

from pyzet.main import main


def test_print_usage(capsys):
    main([])
    out, err = capsys.readouterr()

    assert out.startswith("usage: pyzet")
    assert err == ""


def test_overall_help(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])

    out, err = capsys.readouterr()

    assert out.startswith("usage: pyzet")
    assert err == ""
