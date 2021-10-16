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


def test_list_zets(capsys):
    main(["list", "tests/files/zet"])

    out, err = capsys.readouterr()

    assert out == (
        "2021-10-16 20:51:58 - Zet test entry\n"
        "2021-10-16 22:36:43 - Another zet test entry\n"
    )
    assert err == ""
