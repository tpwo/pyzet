import tempfile
from pathlib import Path

import pytest

from pyzet.constants import CONFIG_FILE, ZETDIR, ZETTEL_FILENAME
from pyzet.main import main

TEST_CFG = f"testing/{CONFIG_FILE}"


def test_no_argv(capsys):
    # It should just print the usage help
    main([])
    out, err = capsys.readouterr()
    assert out.startswith("usage: pyzet")
    assert err == ""


def test_help(capsys):
    with pytest.raises(SystemExit):
        main(["-c", TEST_CFG, "--help"])

    out, err = capsys.readouterr()
    assert out.startswith("usage: pyzet")
    assert err == ""


def test_init_error_folder_exists():
    with pytest.raises(SystemExit) as excinfo:
        main(["-c", TEST_CFG, "init"])
    assert (
        str(excinfo.value) == "ERROR: `testing/zet` folder exists and it's not empty."
    )


def test_init_error_file_exists_at_path():
    with pytest.raises(SystemExit) as excinfo:
        main(["-c", TEST_CFG, "-r", "README.md", "init"])
    assert str(excinfo.value) == "ERROR: `README.md` exists and is a file."


def test_init_error_config_file_missing():
    with pytest.raises(SystemExit) as excinfo:
        main(["-c", "some/nonexistent/path", "init"])
    assert (
        str(excinfo.value)
        == "ERROR: config file at `some/nonexistent/path` not found.\n"
        "Add it or use `--config` flag."
    )


def test_edit_error_editor_not_found():
    with pytest.raises(SystemExit) as excinfo:
        main(["-c", "testing/pyzet-wrong.yaml", "edit"])
    assert str(excinfo.value) == "ERROR: editor `not-vim` cannot be found."


def test_edit_error_missing_repo_in_yaml():
    with pytest.raises(SystemExit) as excinfo:
        main(["-c", "testing/pyzet-missing-repo.yaml", "edit"])
    assert (
        str(excinfo.value)
        == "ERROR: field `repo` missing from `testing/pyzet-missing-repo.yaml`."
    )


def test_show(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "show", "20211016205158"])

    out, err = capsys.readouterr()
    assert out.endswith(
        "# Zet test entry\n\nHello there!\n\nTags:\n\n"
        "    #test-tag #another-tag  #tag-after-two-spaces\n"
    )
    assert err == ""


def test_show_default(capsys):
    # by default, the command shows a zettel with the highest ID (the newest)
    main(["-c", TEST_CFG, "--repo", "testing/zet", "show"])

    out, err = capsys.readouterr()
    assert out.endswith("# Zettel with UTF-8\n\nZażółć gęślą jaźń.\n")
    assert err == ""


def test_show_utf8(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "show", "20220101220852"])

    out, err = capsys.readouterr()
    assert out.endswith("# Zettel with UTF-8\n\nZażółć gęślą jaźń.\n")
    assert err == ""


def test_show_link(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "show", "20211016205158", "--link"])

    out, err = capsys.readouterr()
    assert out == "* [20211016205158](../20211016205158) -- Zet test entry\n"
    assert err == ""


def test_list(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "list"])

    out, err = capsys.readouterr()
    assert out == (
        "20211016205158 -- Zet test entry\n"
        "20211016223643 -- Another zet test entry\n"
        "20220101220852 -- Zettel with UTF-8\n"
    )
    assert err == ""


def test_list_reverse(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "list", "--reverse"])

    out, err = capsys.readouterr()
    assert out == (
        "20220101220852 -- Zettel with UTF-8\n"
        "20211016223643 -- Another zet test entry\n"
        "20211016205158 -- Zet test entry\n"
    )
    assert err == ""


def test_list_pretty(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "list", "--pretty"])

    out, err = capsys.readouterr()
    assert out == (
        "2021-10-16 20:51:58 -- Zet test entry\n"
        "2021-10-16 22:36:43 -- Another zet test entry\n"
        "2022-01-01 22:08:52 -- Zettel with UTF-8\n"
    )
    assert err == ""


def test_list_pretty_reverse(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "list", "--pretty", "--reverse"])

    out, err = capsys.readouterr()
    assert out == (
        "2022-01-01 22:08:52 -- Zettel with UTF-8\n"
        "2021-10-16 22:36:43 -- Another zet test entry\n"
        "2021-10-16 20:51:58 -- Zet test entry\n"
    )
    assert err == ""


def test_list_link(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "list", "--link"])

    out, err = capsys.readouterr()
    assert out == (
        "* [20211016205158](../20211016205158) -- Zet test entry\n"
        "* [20211016223643](../20211016223643) -- Another zet test entry\n"
        "* [20220101220852](../20220101220852) -- Zettel with UTF-8\n"
    )
    assert err == ""


def test_list_link_reverse(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "list", "--link", "--reverse"])

    out, err = capsys.readouterr()
    assert out == (
        "* [20220101220852](../20220101220852) -- Zettel with UTF-8\n"
        "* [20211016223643](../20211016223643) -- Another zet test entry\n"
        "* [20211016205158](../20211016205158) -- Zet test entry\n"
    )
    assert err == ""


def test_list_warning_empty_folder(caplog):
    id_ = "20211016205158"
    id2_ = "20211016205159"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)
        Path(tmpdir, ZETDIR, id2_).mkdir(parents=True)
        with open(Path(tmpdir, ZETDIR, id2_, ZETTEL_FILENAME), "a") as file:
            file.write("# Test")

        main(["-c", TEST_CFG, "--repo", tmpdir, "list"])
        assert f"empty zet folder {id_} detected" in caplog.text


def test_list_error_no_zettels():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR).mkdir(parents=True)
        with pytest.raises(SystemExit) as excinfo:
            main(["-c", TEST_CFG, "--repo", tmpdir, "list"])
        assert str(excinfo.value) == "ERROR: there are no zettels at given repo."


def test_list_wrong_alternative_repo():
    with pytest.raises(SystemExit) as excinfo:
        main(["-c", TEST_CFG, "--repo", "some/nonexistent/path", "list"])
    assert str(excinfo.value).startswith("ERROR: wrong repo path")


def test_tags(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "tags"])

    out, err = capsys.readouterr()
    assert out == "1\t#another-tag\n1\t#tag-after-two-spaces\n2\t#test-tag\n"
    assert err == ""


def test_tags_reverse(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "tags", "--reverse"])

    out, err = capsys.readouterr()
    assert out == "2\t#test-tag\n1\t#tag-after-two-spaces\n1\t#another-tag\n"
    assert err == ""


def test_tags_count(capsys):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "tags", "--count"])

    out, err = capsys.readouterr()
    assert out == "4\n"
    assert err == ""


def test_clean(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["-c", TEST_CFG, "--repo", tmpdir, "clean"])

        out, err = capsys.readouterr()
        assert out == f"will delete {id_}\nUse `--force` to proceed with deletion\n"
        assert err == ""
        assert not Path(tmpdir, id_).exists()


def test_clean_force(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["-c", TEST_CFG, "--repo", tmpdir, "clean", "--force"])

        out, err = capsys.readouterr()
        assert out == f"deleting {id_}\n"
        assert err == ""
        assert not Path(tmpdir, id_).exists()


def test_clean_dry_run(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["-c", TEST_CFG, "--repo", tmpdir, "clean", "--dry-run"])

        out, err = capsys.readouterr()
        assert out == f"will delete {id_}\nUse `--force` to proceed with deletion\n"
        assert err == ""
        assert Path(tmpdir, ZETDIR, id_).exists()


def test_clean_dry_run_and_force(capsys):
    id_ = "20211016205158"
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, ZETDIR, id_).mkdir(parents=True)

        main(["-c", TEST_CFG, "--repo", tmpdir, "clean", "--dry-run", "--force"])

        out, err = capsys.readouterr()
        assert out == f"will delete {id_}\n"
        assert err == ""
        assert Path(tmpdir, ZETDIR, id_).exists()


def test_grep(capfd):
    main(["-c", TEST_CFG, "--repo", "testing/zet", "grep", "hello"])

    out, err = capfd.readouterr()
    line1, line2, _ = out.split("\n")  # 3rd item is an empty str

    assert line1.strip() == "20211016205158/README.md:3:Hello there!"
    assert line2.strip() == "20211016223643/README.md:3:Hello everyone"
    assert err == ""
