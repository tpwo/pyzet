import tempfile
from pathlib import Path

import pytest

from pyzet.main import main


def test_print_usage(capsys):
    main(["--repo", "tests/files/zet"])
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
    main(["--repo", "tests/files/zet", "list"])

    out, err = capsys.readouterr()
    assert (
        out
        == "20211016205158 - Zet test entry\n20211016223643 - Another zet test entry\n"
    )
    assert err == ""


def test_list_zets_pretty(capsys):
    main(["--repo", "tests/files/zet", "list", "--pretty"])

    out, err = capsys.readouterr()
    assert out == (
        "2021-10-16 20:51:58 - Zet test entry\n"
        "2021-10-16 22:36:43 - Another zet test entry\n"
    )
    assert err == ""


def test_show_zet(capsys):
    main(["--repo", "tests/files/zet", "show", "20211016205158"])

    out, err = capsys.readouterr()
    assert out == "# Zet test entry\n\nHello there!\n"
    assert err == ""


def test_list_zets_warning(caplog):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, id_).mkdir()

        main(["--repo", tmpdir, "list"])
        assert f"empty zet folder {id_} detected" in caplog.text


def test_clean_zets(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, id_).mkdir()

        main(["--repo", tmpdir, "clean"])

        out, err = capsys.readouterr()
        assert out == f"deleting {id_}\n"
        assert err == ""
        assert not Path(tmpdir, id_).exists()


def test_clean_zets_dry_run(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, id_).mkdir()

        main(["--repo", tmpdir, "clean", "--dry-run"])

        out, err = capsys.readouterr()
        assert out == f"will delete {id_}\n"
        assert err == ""
        assert Path(tmpdir, id_).exists()


@pytest.mark.skip
def test_add_zet(capsys):
    main(["--repo", "tests/files/zet", "add"])

    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_alternative_repo(capsys):
    main(["--repo", "tests/files/zet"])

    out, err = capsys.readouterr()
    assert out.startswith("usage: pyzet")
    assert err == ""


def test_alternative_repo_wrong():
    with pytest.raises(SystemExit) as excinfo:
        main(["--repo", "some/nonexistent/path"])
    assert str(excinfo.value).startswith("ERROR: wrong repo path")


def test_alternative_repo_wrong_list():
    with pytest.raises(SystemExit) as excinfo:
        main(["--repo", "some/nonexistent/path", "list"])
    assert str(excinfo.value).startswith("ERROR: wrong repo path")
