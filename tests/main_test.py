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
    main(["--config", "tests/files/test-pyzet-config.toml", "list"])

    out, err = capsys.readouterr()

    assert out == (
        "2021-10-16 20:51:58 - Zet test entry\n"
        "2021-10-16 22:36:43 - Another zet test entry\n"
    )
    assert err == ""


def test_show_zet(capsys):
    main(["--config", "tests/files/test-pyzet-config.toml", "show", "20211016205158"])

    out, err = capsys.readouterr()

    assert out == "# Zet test entry\n\nHello there!\n"
    assert err == ""


def test_alternative_config(capsys):
    main(["--config", "tests/files/test-pyzet-config.toml"])

    out, err = capsys.readouterr()

    assert out.startswith("usage: pyzet")
    assert err == ""


def test_wrong_alternative_config(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--config", "README.md"])

    assert str(excinfo.value) == "ERROR: cannot parse the file as TOML"


def test_nonexistent_alternative_config(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--config", "some-nonexistent-file"])

    assert str(excinfo.value) == "ERROR: config file not found on given path"


def test_nonexistent_alternative_config_permission_error(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--config", "."])

    assert str(excinfo.value) == "ERROR: config file not found on given path"
