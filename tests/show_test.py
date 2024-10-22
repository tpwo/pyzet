from __future__ import annotations

import subprocess
from pathlib import Path
from unittest import mock

import pytest

from pyzet import constants as const
from pyzet.main import main
from tests.conftest import TEST_CFG


def test_show(capsys):
    with mock.patch(
        'builtins.input', side_effect=['\n', KeyboardInterrupt]
    ), pytest.raises(SystemExit):
        main([*TEST_CFG, 'show', 'text', '--id', '20211016205158'])

    out, err = capsys.readouterr()
    assert (
        '# Zet test entry\n\nHello there!\n\nTags:\n\n'
        '    #test-tag #another-tag  #tag-after-two-spaces\n'
    ) in out
    assert err == ''


def test_show_default(capsys):
    # by default, the command shows a zettel with the highest ID (the newest)
    with mock.patch(
        'builtins.input', side_effect=['\n', KeyboardInterrupt]
    ), pytest.raises(SystemExit):
        main([*TEST_CFG, 'show', 'text'])

    out, err = capsys.readouterr()
    assert '# Zettel with UTF-8\n\nZażółć gęślą jaźń.\n' in out
    assert err == ''


def test_show_patterns(capsys):
    # TODO: side effect seem to not matter here, namely `\n` also works
    with mock.patch(
        'builtins.input', side_effect=['1', KeyboardInterrupt]
    ), pytest.raises(SystemExit):
        main([*TEST_CFG, 'show', 'text', 'zet', 'test'])
    out, err = capsys.readouterr()
    assert '# Another zet test entry' in out
    assert err == ''


def test_show_patterns_ignore_case(capsys):
    with mock.patch(
        'builtins.input', side_effect=['1', KeyboardInterrupt]
    ), pytest.raises(SystemExit):
        main([*TEST_CFG, 'show', 'text', '--ignore-case', 'zet', 'test'])
    out, err = capsys.readouterr()
    assert '# Zet test entry' in out
    assert err == ''


def test_show_patterns_empty_pattern():
    with pytest.raises(SystemExit) as excinfo:
        main([*TEST_CFG, 'show', 'text', ''])
    (msg,) = excinfo.value.args
    assert msg == 'aborting'


def test_show_patterns_not_matching_pattern(pyzet_init):
    with mock.patch(
        'builtins.input', side_effect=['\n', KeyboardInterrupt]
    ), pytest.raises(SystemExit) as excinfo:
        main([*TEST_CFG, '--repo', pyzet_init, 'show', 'text', 'zet'])
    (msg,) = excinfo.value.args
    assert msg == 'aborting'


def test_show_patterns_empty_repo(pyzet_init):
    with mock.patch(
        'builtins.input', side_effect=['\n', KeyboardInterrupt]
    ), pytest.raises(SystemExit) as excinfo:
        main([*TEST_CFG, '--repo', pyzet_init, 'show', 'text', 'zet'])
    (msg,) = excinfo.value.args
    assert msg == 'aborting'


def test_show_utf8(capsys):
    with mock.patch(
        'builtins.input', side_effect=['\n', KeyboardInterrupt]
    ), pytest.raises(SystemExit):
        main([*TEST_CFG, 'show', 'text', '--id', '20220101220852'])

    out, err = capsys.readouterr()
    assert '# Zettel with UTF-8\n\nZażółć gęślą jaźń.\n' in out
    assert err == ''


def test_show_mdlink(capsys):
    with mock.patch(
        'builtins.input', side_effect=['\n', KeyboardInterrupt]
    ), pytest.raises(SystemExit):
        main([*TEST_CFG, 'show', 'mdlink', '--id', '20211016205158'])

    out, err = capsys.readouterr()
    assert out == '* [20211016205158](../20211016205158) Zet test entry\n'
    assert err == ''


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        (
            'https://github.com/tpwo/pyzet',
            'https://github.com/tpwo/pyzet/tree/main/docs/20211016205159',
        ),
        (
            'https://github.com/tpwo/pyzet.git',
            'https://github.com/tpwo/pyzet/tree/main/docs/20211016205159',
        ),
        (
            'git@github.com:tpwo/pyzet',
            'https://github.com/tpwo/pyzet/tree/main/docs/20211016205159',
        ),
        (
            'git@github.com:tpwo/pyzet.git',
            'https://github.com/tpwo/pyzet/tree/main/docs/20211016205159',
        ),
        (
            'git@gitlab.com:user/repo.git',
            'https://gitlab.com/user/repo/-/tree/main/docs/20211016205159',
        ),
        (
            'git@bitbucket.org:user/repo.git',
            'https://bitbucket.org/user/repo/src/main/docs/20211016205159',
        ),
    ],
)
def test_show_url(raw, expected, pyzet_init, capsys):
    subprocess.run(('git', '-C', pyzet_init, 'remote', 'add', 'origin', raw))
    id_ = '20211016205159'
    test_zettel = Path(pyzet_init, const.ZETDIR, id_)
    test_zettel.mkdir(parents=True)
    with open(Path(test_zettel, const.ZETTEL_FILENAME), 'w') as file:
        file.write('# Test')

    with mock.patch(
        'builtins.input', side_effect=['\n', KeyboardInterrupt]
    ), pytest.raises(SystemExit):
        main([*TEST_CFG, '--repo', pyzet_init, 'show', 'url', '--id', id_])

    out, err = capsys.readouterr()
    assert out == expected + '\n'
    assert err == ''
