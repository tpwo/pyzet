from __future__ import annotations

import pytest

from pyzet.main import main
from pyzet.sample_config import sample_config
from tests.conftest import TEST_CFG

_header = """\
# See https://github.com/tpwo/pyzet for more information.
#
# Put this file at\
"""


def test_sample_config_unix(capsys):
    main([*TEST_CFG, 'sample-config', 'unix'])
    out, err = capsys.readouterr()

    # The assertion is split, because there is one line which is
    # generated dynamically.
    assert out.startswith(_header)
    assert out.endswith(
        """\
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: /usr/bin/vim
editor_args: []
"""
    )
    assert err == ''


def test_sample_config_windows(capsys):
    main([*TEST_CFG, 'sample-config', 'windows'])
    out, err = capsys.readouterr()

    # The assertion is split, because there is one line which is
    # generated dynamically.
    assert out.startswith(_header)
    assert out.endswith(
        """\
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: C:/Program Files/Git/usr/bin/vim.exe
editor_args: []
"""
    )
    assert err == ''


def test_sample_error(capsys):
    with pytest.raises(SystemExit):
        main([*TEST_CFG, 'sample-config', 'foobar'])

    out, err = capsys.readouterr()
    assert out == ''
    assert (
        "pyzet sample-config: error: argument kind: invalid choice: 'foobar'"
        in err
    )


def test_sample_error_direct():
    with pytest.raises(NotImplementedError) as excinfo:
        sample_config(kind='foobar')
    (msg,) = excinfo.value.args
    assert msg == "ERROR: sample config kind 'foobar' not recognized."
