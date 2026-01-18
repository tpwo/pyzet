from __future__ import annotations

from os import getenv as getenv_original
from unittest import mock

import pytest

from pyzet.main import main
from pyzet.utils import get_default_editor
from tests.conftest import TEST_CFG


def test_sample_config(capsys):
    with (
        mock.patch('pyzet.utils.DEFAULT_CFG_LOCATION', new='<config-loc>'),
        mock.patch('os.getenv', return_value='<editor>'),
    ):
        main([*TEST_CFG, 'sample-config'])
    out, err = capsys.readouterr()

    assert err == ''
    assert (
        out
        == """\
# See https://github.com/tpwo/pyzet for more information.
#
# Put this file at <config-loc>
# Below options use global paths, but feel free
# to use program name directly if it's on your PATH.
repo: ~/zet
editor: <editor>
editor_args: []
"""
    )


def test_sample_error():
    with (
        mock.patch('os.getenv', return_value=None),
        pytest.raises(SystemExit) as excinfo,
    ):
        main([*TEST_CFG, 'sample-config'])

    (msg,) = excinfo.value.args
    assert (
        'ERROR: cannot get the default editor\n'
        'Define `EDITOR` or `VISUAL` env var or configure `editor` in' in msg
    )


def mock_os_getenv(envvar: str, default: str | None = None) -> str | None:
    """Simulate situation when VISUAL is defined and EDITOR is missing."""
    if envvar == 'EDITOR':
        return None
    elif envvar == 'VISUAL':
        return '<editor>'
    else:
        # os.getenv is patched, so we have to import it under changed name
        return getenv_original(envvar, default)


def test_get_default_editor_visual_envvar():
    with mock.patch('os.getenv', new=mock_os_getenv):
        out = get_default_editor()
        assert out == '<editor>'
