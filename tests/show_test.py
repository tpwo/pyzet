from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from pyzet import constants as const
from pyzet.main import main
from tests.conftest import TEST_CFG


def test_mdlink(capsys):
    main([*TEST_CFG, 'mdlink', '--id', '20211016205158'])

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
def test_url(raw, expected, pyzet_init, capsys):
    subprocess.run(('git', '-C', pyzet_init, 'remote', 'add', 'origin', raw))
    id_ = '20211016205159'
    test_zettel = Path(pyzet_init, const.ZETDIR, id_)
    test_zettel.mkdir(parents=True)
    with open(Path(test_zettel, const.ZETTEL_FILENAME), 'w') as file:
        file.write('# Test')

    main([*TEST_CFG, '--repo', pyzet_init, 'url', '--id', id_])

    out, err = capsys.readouterr()
    assert out == expected + '\n'
    assert err == ''
