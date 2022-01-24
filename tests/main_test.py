import sys
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
    assert out == (
        "20211016205158 - Zet test entry\n"
        "20211016223643 - Another zet test entry\n"
        "20220101220852 - Zettel with UTF-8\n"
    )
    assert err == ""


def test_list_zettels_reverse(capsys):
    main(["--repo", "testing/zet", "list", "--reverse"])

    out, err = capsys.readouterr()
    assert out == (
        "20220101220852 - Zettel with UTF-8\n"
        "20211016223643 - Another zet test entry\n"
        "20211016205158 - Zet test entry\n"
    )
    assert err == ""


def test_list_tags(capsys):
    main(["--repo", "testing/zet", "tags"])

    out, err = capsys.readouterr()
    assert out == "1\t#another-tag\n1\t#tag-after-two-spaces\n2\t#test-tag\n"
    assert err == ""


def test_list_tags_reverse(capsys):
    main(["--repo", "testing/zet", "tags", "--reverse"])

    out, err = capsys.readouterr()
    assert out == "2\t#test-tag\n1\t#tag-after-two-spaces\n1\t#another-tag\n"
    assert err == ""


def test_list_tags_count(capsys):
    main(["--repo", "testing/zet", "tags", "--count"])

    out, err = capsys.readouterr()
    assert out == "4\n"
    assert err == ""


def test_list_zettels_pretty(capsys):
    main(["--repo", "testing/zet", "list", "--pretty"])

    out, err = capsys.readouterr()
    assert out == (
        "2021-10-16 20:51:58 - Zet test entry\n"
        "2021-10-16 22:36:43 - Another zet test entry\n"
        "2022-01-01 22:08:52 - Zettel with UTF-8\n"
    )
    assert err == ""


def test_list_zettels_pretty_reverse(capsys):
    main(["--repo", "testing/zet", "list", "--pretty", "--reverse"])

    out, err = capsys.readouterr()
    assert out == (
        "2022-01-01 22:08:52 - Zettel with UTF-8\n"
        "2021-10-16 22:36:43 - Another zet test entry\n"
        "2021-10-16 20:51:58 - Zet test entry\n"
    )
    assert err == ""


def test_show_zettel(capsys):
    main(["--repo", "testing/zet", "show", "20211016205158"])

    out, err = capsys.readouterr()
    assert out.endswith(
        "# Zet test entry\n\nHello there!\n\nTags:\n\n"
        "    #test-tag #another-tag  #tag-after-two-spaces\n"
    )
    assert err == ""


def test_show_zettel_default(capsys):
    # by default, the command shows a zettel with the highest ID (the newest)
    main(["--repo", "testing/zet", "show"])

    out, err = capsys.readouterr()
    assert out.endswith("# Zettel with UTF-8\n\nZażółć gęślą jaźń.\n")
    assert err == ""


def test_show_zettel_utf8(capsys):
    main(["--repo", "testing/zet", "show", "20220101220852"])

    out, err = capsys.readouterr()
    assert out.endswith("# Zettel with UTF-8\n\nZażółć gęślą jaźń.\n")
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
        assert out == f"will delete {id_}\nUse `--force` to proceed with deletion\n"
        assert err == ""
        assert not Path(tmpdir, id_).exists()


def test_clean_zettels_force(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["--repo", tmpdir, "clean", "--force"])

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
        assert out == f"will delete {id_}\nUse `--force` to proceed with deletion\n"
        assert err == ""
        assert Path(tmpdir, ZETDIR, id_).exists()


def test_clean_zettels_dry_run_and_force(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["--repo", tmpdir, "clean", "--dry-run", "--force"])

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


@pytest.mark.skipif(
    sys.platform != "win32", reason="fails on Linux due to different grep behavior"
)
def test_grep_win(capfd):
    main(["--repo", "testing/zet", "grep", "hello"])

    out, err = capfd.readouterr()
    line1, line2, _ = out.split("\n")  # 3rd item is an empty str

    assert line1.endswith("zettels/20211016205158/README.md:3:Hello there!")
    assert line2.endswith("zettels/20211016223643/README.md:3:Hello everyone")
    assert err == ""


@pytest.mark.skipif(
    sys.platform == "win32", reason="fails on Windows due to different grep behavior"
)
def test_grep_unix(capfd):
    main(["--repo", "testing/zet", "grep", "hello"])

    out, err = capfd.readouterr()
    line1, line2, _ = out.split("\n")  # 3rd item is an empty str

    assert line1.endswith("zettels/20211016223643/README.md:3:Hello everyone")
    assert line2.endswith("zettels/20211016205158/README.md:3:Hello there!")
    assert err == ""
