import pyzet.constants as C
from pyzet.main import main

GREP_CMD = ("--config", f"testing/{C.CONFIG_FILE}", "grep")


def test_grep(capfd):
    main([*GREP_CMD, "hello"])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
Hello there!

20211016223643/README.md
Hello everyone
"""
    assert out == expected
    assert err == ""


def test_grep_title(capfd):
    main([*GREP_CMD, "--title", "hello"])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
# Zet test entry
Hello there!

20211016223643/README.md
# Another zet test entry
Hello everyone
"""
    assert out == expected
    assert err == ""


def test_grep_line_number(capfd):
    main([*GREP_CMD, "--line-number", "hello"])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
3:Hello there!

20211016223643/README.md
3:Hello everyone
"""
    assert out == expected
    assert err == ""


def test_grep_title_and_line_number(capfd):
    main([*GREP_CMD, "--title", "--line-number", "hello"])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
1:# Zet test entry
3:Hello there!

20211016223643/README.md
1:# Another zet test entry
3:Hello everyone
"""
    assert out == expected
    assert err == ""


def test_grep_multiple_matches_in_file(capfd):
    main([*GREP_CMD, "test"])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
# Zet test entry
    #test-tag #another-tag  #tag-after-two-spaces

20211016223643/README.md
# Another zet test entry
    #test-tag
"""
    assert out == expected
    assert err == ""


def test_grep_multiple_matches_in_file_title(capfd):
    # Title matches searched pattern, so --title doesn't make a difference.
    main([*GREP_CMD, "--title", "test"])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
# Zet test entry
    #test-tag #another-tag  #tag-after-two-spaces

20211016223643/README.md
# Another zet test entry
    #test-tag
"""
    assert out == expected
    assert err == ""


def test_grep_multiple_matches_in_file_line_number(capfd):
    main([*GREP_CMD, "--line-number", "test"])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
1:# Zet test entry
7:    #test-tag #another-tag  #tag-after-two-spaces

20211016223643/README.md
1:# Another zet test entry
7:    #test-tag
"""
    assert out == expected
    assert err == ""


def test_grep_multiple_matches_in_file_title_and_line_number(capfd):
    # Title matches searched pattern, so --title doesn't make a difference.
    main([*GREP_CMD, "--title", "--line-number", "test"])

    out, err = capfd.readouterr()
    expected = """\
20211016205158/README.md
1:# Zet test entry
7:    #test-tag #another-tag  #tag-after-two-spaces

20211016223643/README.md
1:# Another zet test entry
7:    #test-tag
"""
    assert out == expected
    assert err == ""


def test_grep_with_options(capfd):
    main([*GREP_CMD, "everyone", "--", "--or", "-e", "test-tag"])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
Hello everyone
    #test-tag
"""
    assert out == expected
    assert err == ""


def test_grep_title_with_options(capfd):
    main([*GREP_CMD, "--title", "everyone", "--", "--or", "-e", "test-tag"])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
# Another zet test entry
Hello everyone
    #test-tag
"""
    assert out == expected
    assert err == ""


def test_grep_line_number_with_options(capfd):
    main([*GREP_CMD, "--line-number", "everyone", "--", "--or", "-e", "test-tag"])

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
3:Hello everyone
7:    #test-tag
"""
    assert out == expected
    assert err == ""


def test_grep_title_and_line_number_with_options(capfd):
    main(
        [
            *GREP_CMD,
            "--title",
            "--line-number",
            "everyone",
            "--",
            "--or",
            "-e",
            "test-tag",
        ]
    )

    out, err = capfd.readouterr()
    expected = """\
20211016223643/README.md
1:# Another zet test entry
3:Hello everyone
7:    #test-tag
"""
    assert out == expected
    assert err == ""
