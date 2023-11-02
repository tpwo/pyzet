from __future__ import annotations

import pytest

import pyzet.constants as C
from pyzet.main import main

GREP_CMD = ('--config', f'testing/{C.CONFIG_FILE}', 'grep')


def test_grep(capfd):
    main([*GREP_CMD, 'zet'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
# Another zet test entry
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_ignore_case(capfd):
    main([*GREP_CMD, '--ignore-case', 'zet'])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
# Zet test entry

20211016223643/README.md
# Another zet test entry

20220101220852/README.md
# Zettel with UTF-8
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_title(capfd):
    main([*GREP_CMD, '--title', 'Hello'])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
# Zet test entry
Hello there!

20211016223643/README.md
# Another zet test entry
Hello everyone
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_line_number(capfd):
    main([*GREP_CMD, '--line-number', 'Hello'])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
3:Hello there!

20211016223643/README.md
3:Hello everyone
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_title_and_line_number(capfd):
    main([*GREP_CMD, '--title', '--line-number', 'Hello'])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
1:# Zet test entry
3:Hello there!

20211016223643/README.md
1:# Another zet test entry
3:Hello everyone
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_multiple_matches_in_file(capfd):
    main([*GREP_CMD, 'test'])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
# Zet test entry
    #test-tag #another-tag  #tag-after-two-spaces

20211016223643/README.md
# Another zet test entry
    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_multiple_matches_in_file_title(capfd):
    # Title matches searched pattern, so --title doesn't make a difference.
    main([*GREP_CMD, '--title', 'test'])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
# Zet test entry
    #test-tag #another-tag  #tag-after-two-spaces

20211016223643/README.md
# Another zet test entry
    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_multiple_matches_in_file_line_number(capfd):
    main([*GREP_CMD, '--line-number', 'test'])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
1:# Zet test entry
7:    #test-tag #another-tag  #tag-after-two-spaces

20211016223643/README.md
1:# Another zet test entry
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_multiple_matches_in_file_title_and_line_number(capfd):
    # Title matches searched pattern, so --title doesn't make a difference.
    main([*GREP_CMD, '--title', '--line-number', 'test'])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
1:# Zet test entry
7:    #test-tag #another-tag  #tag-after-two-spaces

20211016223643/README.md
1:# Another zet test entry
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_two_patterns(capfd):
    main([*GREP_CMD, 'everyone', 'test-tag'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
Hello everyone
    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_three_patterns(capfd):
    main([*GREP_CMD, 'everyone', 'test-tag', 'zet'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
# Another zet test entry
Hello everyone
    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_three_patterns_verbose(capfd):
    main([*GREP_CMD, 'everyone', 'test-tag', '--', '--or', '-e', 'zet'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
# Another zet test entry
Hello everyone
    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_two_patterns_line_number(capfd):
    main([*GREP_CMD, '--line-number', 'everyone', 'test-tag'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
3:Hello everyone
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_two_patterns_line_number_last(capfd):
    main([*GREP_CMD, 'everyone', 'test-tag', '--line-number'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
3:Hello everyone
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_two_patterns_error_argparse(capfd):
    with pytest.raises(SystemExit):
        main([*GREP_CMD, 'everyone', '--line-number', 'test-tag'])

    out, err = capfd.readouterr()
    assert out == ''
    assert err.endswith('pyzet: error: unrecognized arguments: test-tag\n')


def test_grep_two_patterns_error_argparse_weird(capfd):
    # I'm not sure why it fails, but it does, so this test confirms it.
    with pytest.raises(SystemExit):
        main([*GREP_CMD, 'everyone', 'test-tag', '-n', '--', '--no-color'])

    out, err = capfd.readouterr()
    assert out == ''
    assert err.endswith(
        'pyzet: error: unrecognized arguments: -- --no-color\n'
    )


def test_grep_title_with_options_error_weird(capfd):
    # I'm not sure why it fails, but it does, so this test confirms it.
    #
    # The only difference between this one and test_grep_title_with_options()
    # is the order of arguments.
    with pytest.raises(SystemExit):
        main([*GREP_CMD, 'everyone', '-t', '--', '--or', '-e', 'test-tag'])

    out, err = capfd.readouterr()
    assert out == ''
    assert err.endswith(
        'pyzet: error: unrecognized arguments: -- --or -e test-tag\n'
    )


def test_grep_two_patterns_line_number_verbose(capfd):
    main([*GREP_CMD, 'everyone', 'test-tag', '--', '--line-number'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
3:Hello everyone
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_multiple_patterns_line_number(capfd):
    main([*GREP_CMD, 'everyone', 'test-tag', '--', '-n', '--or', '-e', 'zet'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
1:# Another zet test entry
3:Hello everyone
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_multiple_patterns_line_number_different_order(capfd):
    main([*GREP_CMD, 'everyone', 'test-tag', '--', '--or', '-e', 'zet', '-n'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
1:# Another zet test entry
3:Hello everyone
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_with_option_and_pattern(capfd):
    # --and means that matching line should always have its pattern
    main([*GREP_CMD, '-ti', 'zet', '--', '--and', '-e', 'another'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
# Another zet test entry
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_line_number_with_options(capfd):
    main([*GREP_CMD, '-n', 'everyone', '--', '--or', '-e', 'test-tag'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
3:Hello everyone
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''


def test_grep_title_and_line_number_with_options(capfd):
    main([*GREP_CMD, '-tn', 'everyone', '--', '--or', '-e', 'test-tag'])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
1:# Another zet test entry
3:Hello everyone
7:    #test-tag
"""
    assert out.replace('\r', '') == expected
    assert err == ''
