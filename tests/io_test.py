import shlex
from pathlib import Path

import freezegun
import pytest

from pyzet.main import _open_file
from pyzet.main import add_zettel
from pyzet.main import edit_zettel
from pyzet.main import init_repo
from pyzet.utils import Config


def get_fake_editor(path: Path, output: str) -> str:
    """Creates a fake editor returning given output and return path to it."""
    # TODO: path of fake editor should be dynamic to avoid overwriting
    fake_editor_path = path / 'fake_editor'
    with open(fake_editor_path, 'w') as f:
        f.write(f'#!/bin/sh\necho {shlex.quote(output)} > $1\n')
    fake_editor_path.chmod(0o755)
    return fake_editor_path.as_posix()


def test_open_file_saves_string_to_file(tmp_path):
    fake_editor = get_fake_editor(tmp_path, 'Hello World!')
    filename = Path(tmp_path, 'test_file')
    _open_file(filename, fake_editor)

    with open(filename) as f:
        assert f.read() == 'Hello World!\n'


def test_open_file_file_not_found(tmp_path):
    fake_editor = get_fake_editor(tmp_path, 'Hello World!')
    filename = Path('/this/does-not/exist')
    with pytest.raises(SystemExit) as excinfo:
        _open_file(filename, fake_editor)
    (msg,) = excinfo.value.args
    assert "ERROR: problem opening '/this/does-not/exist'" in msg


@freezegun.freeze_time('2005-04-02 21:37:01')
def test_add_zettel(tmp_path):
    fake_editor = get_fake_editor(tmp_path, '# Created by a fake editor')
    cfg = Config(repo=tmp_path, editor=fake_editor)
    add_zettel(cfg)
    zettel = tmp_path / 'zettels' / '20050402213701' / 'README.md'
    with open(zettel) as f:
        assert f.read() == '# Created by a fake editor\n'


@freezegun.freeze_time('2005-04-02 21:37:01')
def test_edit_zettel(tmp_path, caplog):
    import logging

    caplog.set_level(logging.DEBUG)
    id_ = '20050402213701'
    fake_editor = get_fake_editor(tmp_path, '# A test zettel')
    cfg = Config(repo=tmp_path / 'zet-repo', editor=fake_editor)
    init_repo(cfg, branch_name='main')
    add_zettel(cfg)

    fake_editor2 = get_fake_editor(tmp_path, '# Edited by a fake editor')
    cfg2 = Config(repo=tmp_path / 'zet-repo', editor=fake_editor2)
    edit_zettel(id_, cfg2)
    zettel = tmp_path / 'zet-repo' / 'zettels' / '20050402213701' / 'README.md'
    with open(zettel) as f:
        assert f.read() == '# Edited by a fake editor\n'


@freezegun.freeze_time('2005-04-02 21:37:01')
def test_edit_zettel_no_changes(tmp_path, caplog):
    import logging

    caplog.set_level(logging.DEBUG)
    id_ = '20050402213701'
    fake_editor = get_fake_editor(tmp_path, '# A test zettel')
    cfg = Config(repo=tmp_path / 'zet-repo', editor=fake_editor)
    init_repo(cfg, branch_name='main')
    add_zettel(cfg)

    edit_zettel(id_, cfg)
    zettel = tmp_path / 'zet-repo' / 'zettels' / '20050402213701' / 'README.md'
    with open(zettel) as f:
        assert f.read() == '# A test zettel\n'
