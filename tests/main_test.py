import tempfile
from pathlib import Path

import pytest

from pyzet.constants import ZETDIR
from pyzet.main import main


def test_print_usage(capsys):
    main(["--repo", "testing/zet"])
    out, err = capsys.readouterr()
    assert out.startswith("usage: pyzet")
    assert err == ""


def test_overall_help(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])

    out, err = capsys.readouterr()
    assert out.startswith("usage: pyzet")
    assert err == ""


def test_list_zettels(capsys):
    main(["--repo", "testing/zet", "list"])

    out, err = capsys.readouterr()
    assert (
        out
        == "20211016205158 - Zet test entry\n20211016223643 - Another zet test entry\n"
    )
    assert err == ""


def test_list_zettels_reverse(capsys):
    main(["--repo", "testing/zet", "list", "--reverse"])

    out, err = capsys.readouterr()
    assert (
        out
        == "20211016223643 - Another zet test entry\n20211016205158 - Zet test entry\n"
    )
    assert err == ""


def test_list_tags(capsys):
    main(["--repo", "testing/zet", "tags"])

    out, err = capsys.readouterr()
    assert out == "1\t#another-tag\n1\t#tag-after-two-spaces\n1\t#test-tag\n"
    assert err == ""


def test_list_tags_reverse(capsys):
    main(["--repo", "testing/zet", "tags", "--reverse"])

    out, err = capsys.readouterr()
    assert out == "1\t#test-tag\n1\t#tag-after-two-spaces\n1\t#another-tag\n"
    assert err == ""


def test_list_tags_count(capsys):
    main(["--repo", "testing/zet", "tags", "--count"])

    out, err = capsys.readouterr()
    assert out == "3\n"
    assert err == ""


def test_list_zettels_pretty(capsys):
    main(["--repo", "testing/zet", "list", "--pretty"])

    out, err = capsys.readouterr()
    assert out == (
        "2021-10-16 20:51:58 - Zet test entry\n"
        "2021-10-16 22:36:43 - Another zet test entry\n"
    )
    assert err == ""


def test_list_zettels_pretty_reverse(capsys):
    main(["--repo", "testing/zet", "list", "--pretty", "--reverse"])

    out, err = capsys.readouterr()
    assert out == (
        "2021-10-16 22:36:43 - Another zet test entry\n"
        "2021-10-16 20:51:58 - Zet test entry\n"
    )
    assert err == ""


def test_show_zettel(capsys):
    main(["--repo", "testing/zet", "show", "20211016205158"])

    out, err = capsys.readouterr()
    assert (
        out == "# Zet test entry\n\nHello there!\n\nTags:\n\n"
        "    #test-tag #another-tag  #tag-after-two-spaces\n"
    )
    assert err == ""


def test_show_zettel_default(capsys):
    main(["--repo", "testing/zet", "show"])

    out, err = capsys.readouterr()
    assert out == "# Another zet test entry\n\nHello everyone\n"
    assert err == ""


def test_list_zettels_warning(caplog):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["--repo", tmpdir, "list"])
        assert f"empty zet folder {id_} detected" in caplog.text


def test_clean_zettels(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["--repo", tmpdir, "clean"])

        out, err = capsys.readouterr()
        assert out == f"deleting {id_}\n"
        assert err == ""
        assert not Path(tmpdir, id_).exists()


def test_clean_zettels_dry_run(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["--repo", tmpdir, "clean", "--dry-run"])

        out, err = capsys.readouterr()
        assert out == f"will delete {id_}\n"
        assert err == ""
        assert Path(tmpdir, ZETDIR, id_).exists()


def test_alternative_repo(capsys):
    main(["--repo", "testing/zet"])

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
