from pyzet.sample_config import sample_config


def test_sample_config(capsys):
    ret = sample_config()
    assert ret == 0
    out, _ = capsys.readouterr()

    # The assertion is split, because there is one line which is generated dynamically.
    assert out.startswith(
        """\
# See https://github.com/wojdatto/pyzet.git for more information.
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
