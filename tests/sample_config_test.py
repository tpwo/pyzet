import pytest

from pyzet.main import main
from pyzet.sample_config import sample_config
from testing.constants import TEST_CFG


def test_sample_config_unix(capsys):
    main([*TEST_CFG, "sample-config", "unix"])
    out, err = capsys.readouterr()

    # The assertion is split, because there is one line which is generated dynamically.
    assert out.startswith(
        """\
# See https://github.com/wojdatto/pyzet for more information.
#
# Put this file at\
"""
    )
    assert out.endswith(
        """\
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: /usr/bin/vim
git: /usr/bin/git
"""
    )
    assert err == ""


def test_sample_config_windows(capsys):
    main([*TEST_CFG, "sample-config", "windows"])
    out, err = capsys.readouterr()

    # The assertion is split, because there is one line which is generated dynamically.
    assert out.startswith(
        """\
# See https://github.com/wojdatto/pyzet for more information.
#
# Put this file at\
"""
    )
    assert out.endswith(
        """\
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: C:/Program Files/Git/usr/bin/vim.exe
git: C:/Program Files/Git/cmd/git.exe
"""
    )
    assert err == ""


def test_sample_error(capsys):
    with pytest.raises(SystemExit):
        main([*TEST_CFG, "sample-config", "foobar"])

    out, err = capsys.readouterr()
    assert out == ""
    assert err.endswith(
        "pyzet sample-config: error: argument kind: invalid choice: "
        "'foobar' (choose from 'unix', 'windows')\n"
    )


def test_sample_error_direct():
    with pytest.raises(NotImplementedError) as excinfo:
        sample_config(kind="foobar")
    assert str(excinfo.value) == "ERROR: sample config kind 'foobar' not recognized."
