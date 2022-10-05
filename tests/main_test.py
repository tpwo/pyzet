import logging
from pathlib import Path

import pytest

import pyzet.constants as C
from pyzet.main import main
from testing.constants import TEST_CFG


def test_no_argv(capsys):
    # It should just print the usage help
    main([])
    out, err = capsys.readouterr()
    assert out.startswith('usage: pyzet')
    assert err == ''


def test_help(capsys):
    with pytest.raises(SystemExit):
        main([*TEST_CFG, '--help'])

    out, err = capsys.readouterr()
    assert out.startswith('usage: pyzet')
    assert err == ''


def test_init_repo_flag(tmp_path, capfd, caplog):
    caplog.set_level(logging.INFO)

    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'init'])

    out, err = capfd.readouterr()
    assert tmp_path.name in out
    assert err == ''
    assert f"init: create git repo '{tmp_path}'" in caplog.text
    assert Path(tmp_path, C.ZETDIR).exists()


def test_init_repo_flag_custom_branch(tmp_path, capfd, caplog):
    caplog.set_level(logging.INFO)
    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'init', '-b', 'foobar'])

    out, err = capfd.readouterr()
    assert tmp_path.name in out
    assert err == ''
    assert f"init: create git repo '{tmp_path}'" in caplog.text
    assert Path(tmp_path, C.ZETDIR).exists()

    # Verify if the branch name was assigned correctly
    # by checking `pyzet status` output.
    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'status'])
    out, err = capfd.readouterr()
    assert out.startswith('On branch foobar')
    assert err == ''


def test_init_custom_target(tmp_path, capfd, caplog):
    caplog.set_level(logging.INFO)
    main([*TEST_CFG, 'init', tmp_path.as_posix()])

    out, err = capfd.readouterr()
    assert Path(tmp_path).name in out
    assert err == ''
    assert f"init: create git repo '{tmp_path}'" in caplog.text
    assert Path(tmp_path, C.ZETDIR).exists()


def test_init_custom_target_custom_branch(tmp_path, capfd, caplog):
    caplog.set_level(logging.INFO)
    main([*TEST_CFG, 'init', tmp_path.as_posix(), '-b', 'foobar'])

    out, err = capfd.readouterr()
    assert tmp_path.name in out
    assert err == ''
    assert f"init: create git repo '{tmp_path}'" in caplog.text
    assert Path(tmp_path, C.ZETDIR).exists()

    # Verify if the branch name was assigned correctly
    # by checking `pyzet status` output.
    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'status'])
    out, err = capfd.readouterr()
    assert out.startswith('On branch foobar')
    assert err == ''


def test_init_repo_flag_and_custom_target(tmp_path, capfd, caplog):
    # Custom target should be preferred over repo passed with '--repo'
    caplog.set_level(logging.INFO)
    repo_dir = Path(tmp_path, 'repo-dir')
    init_dir = Path(tmp_path, 'init-dir')
    main([*TEST_CFG, '-r', repo_dir.as_posix(), 'init', init_dir.as_posix()])

    out, err = capfd.readouterr()
    assert init_dir.name in out
    assert err == ''
    assert f"init: create git repo '{init_dir}'" in caplog.text
    assert Path(init_dir, C.ZETDIR).exists()
    assert not Path(repo_dir, C.ZETDIR).exists()


def test_init_error_folder_exists():
    with pytest.raises(SystemExit) as excinfo:
        main([*TEST_CFG, 'init'])
    assert (
        str(excinfo.value)
        == "ERROR: 'testing/zet' folder exists and it's not empty."
    )


def test_init_error_file_exists_at_path():
    with pytest.raises(SystemExit) as excinfo:
        main([*TEST_CFG, '-r', 'README.md', 'init'])
    assert str(excinfo.value) == "ERROR: 'README.md' exists and is a file."


def test_init_error_config_file_missing():
    with pytest.raises(SystemExit) as excinfo:
        main(['-c', 'some/nonexistent/path', 'init'])
    assert (
        str(excinfo.value)
        == "ERROR: config file at 'some/nonexistent/path' not found.\n"
        "Add it or use '--config' flag."
    )


def test_edit_error_editor_not_found():
    with pytest.raises(SystemExit) as excinfo:
        main(['-c', 'testing/pyzet-wrong.yaml', 'edit'])
    assert str(excinfo.value) == "ERROR: editor 'not-vim' cannot be found."


def test_edit_error_missing_repo_in_yaml():
    with pytest.raises(SystemExit) as excinfo:
        main(['-c', 'testing/pyzet-missing-repo.yaml', 'edit'])
    assert (
        str(excinfo.value) == "ERROR: field 'repo' missing from"
        " 'testing/pyzet-missing-repo.yaml'."
    )


def test_show(capsys):
    main([*TEST_CFG, 'show', '20211016205158'])

    out, err = capsys.readouterr()
    assert out.endswith(
        '# Zet test entry\n\nHello there!\n\nTags:\n\n'
        '    #test-tag #another-tag  #tag-after-two-spaces\n'
    )
    assert err == ''


def test_show_default(capsys):
    # by default, the command shows a zettel with the highest ID (the newest)
    main([*TEST_CFG, 'show'])

    out, err = capsys.readouterr()
    assert out.endswith('# Zettel with UTF-8\n\nZażółć gęślą jaźń.\n')
    assert err == ''


def test_show_utf8(capsys):
    main([*TEST_CFG, 'show', '20220101220852'])

    out, err = capsys.readouterr()
    assert out.endswith('# Zettel with UTF-8\n\nZażółć gęślą jaźń.\n')
    assert err == ''


def test_show_link(capsys):
    main([*TEST_CFG, 'show', '20211016205158', '--link'])

    out, err = capsys.readouterr()
    assert out == '* [20211016205158](../20211016205158) Zet test entry\n'
    assert err == ''


def test_list(capsys):
    main([*TEST_CFG, 'list'])

    out, err = capsys.readouterr()
    assert out == (
        '20211016205158 -- Zet test entry\n'
        '20211016223643 -- Another zet test entry\n'
        '20220101220852 -- Zettel with UTF-8\n'
    )
    assert err == ''


def test_list_reverse(capsys):
    main([*TEST_CFG, 'list', '--reverse'])

    out, err = capsys.readouterr()
    assert out == (
        '20220101220852 -- Zettel with UTF-8\n'
        '20211016223643 -- Another zet test entry\n'
        '20211016205158 -- Zet test entry\n'
    )
    assert err == ''


def test_list_pretty(capsys):
    main([*TEST_CFG, 'list', '--pretty'])

    out, err = capsys.readouterr()
    assert out == (
        '2021-10-16 20:51:58 -- Zet test entry\n'
        '2021-10-16 22:36:43 -- Another zet test entry\n'
        '2022-01-01 22:08:52 -- Zettel with UTF-8\n'
    )
    assert err == ''


def test_list_pretty_reverse(capsys):
    main([*TEST_CFG, 'list', '--pretty', '--reverse'])

    out, err = capsys.readouterr()
    assert out == (
        '2022-01-01 22:08:52 -- Zettel with UTF-8\n'
        '2021-10-16 22:36:43 -- Another zet test entry\n'
        '2021-10-16 20:51:58 -- Zet test entry\n'
    )
    assert err == ''


def test_list_link(capsys):
    main([*TEST_CFG, 'list', '--link'])

    out, err = capsys.readouterr()
    assert out == (
        '* [20211016205158](../20211016205158) Zet test entry\n'
        '* [20211016223643](../20211016223643) Another zet test entry\n'
        '* [20220101220852](../20220101220852) Zettel with UTF-8\n'
    )
    assert err == ''


def test_list_link_reverse(capsys):
    main([*TEST_CFG, 'list', '--link', '--reverse'])

    out, err = capsys.readouterr()
    assert out == (
        '* [20220101220852](../20220101220852) Zettel with UTF-8\n'
        '* [20211016223643](../20211016223643) Another zet test entry\n'
        '* [20211016205158](../20211016205158) Zet test entry\n'
    )
    assert err == ''


def test_list_warning_empty_folder(tmp_path, caplog):
    id_ = '20211016205158'
    Path(tmp_path, C.ZETDIR, id_).mkdir(parents=True)

    zettel2 = Path(tmp_path, C.ZETDIR, '20211016205159')
    zettel2.mkdir(parents=True)
    with open(Path(zettel2, C.ZETTEL_FILENAME), 'w') as file:
        file.write('# Test')

    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'list'])
    assert f'empty zet folder {id_} detected' in caplog.text


def test_list_error_no_zettels(tmp_path):
    Path(tmp_path, C.ZETDIR).mkdir(parents=True)
    with pytest.raises(SystemExit) as excinfo:
        main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'list'])
    assert str(excinfo.value) == 'ERROR: there are no zettels at given repo.'


def test_list_wrong_alternative_repo():
    with pytest.raises(SystemExit) as excinfo:
        main([*TEST_CFG, '--repo', 'some/nonexistent/path', 'list'])
    assert str(excinfo.value).startswith('ERROR: wrong repo path')


def test_tags(capsys):
    main([*TEST_CFG, 'tags'])

    out, err = capsys.readouterr()
    assert out == '1\t#another-tag\n1\t#tag-after-two-spaces\n2\t#test-tag\n'
    assert err == ''


def test_tags_reverse(capsys):
    main([*TEST_CFG, 'tags', '--reverse'])

    out, err = capsys.readouterr()
    assert out == '2\t#test-tag\n1\t#tag-after-two-spaces\n1\t#another-tag\n'
    assert err == ''


def test_tags_count(capsys):
    main([*TEST_CFG, 'tags', '--count'])

    out, err = capsys.readouterr()
    assert out == '4\n'
    assert err == ''


def test_clean(tmp_path, capsys):
    id_ = '20211016205158'
    Path(tmp_path, C.ZETDIR, id_).mkdir(parents=True)

    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'clean'])

    out, err = capsys.readouterr()
    assert (
        out == f"will delete {id_}\nUse '--force' to proceed with deletion\n"
    )
    assert err == ''
    assert not Path(tmp_path, id_).exists()


def test_clean_force(tmp_path, capsys):
    id_ = '20211016205158'
    Path(tmp_path, C.ZETDIR, id_).mkdir(parents=True)

    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'clean', '--force'])

    out, err = capsys.readouterr()
    assert out == f'deleting {id_}\n'
    assert err == ''
    assert not Path(tmp_path, id_).exists()


def test_clean_dry_run(tmp_path, capsys):
    id_ = '20211016205158'
    Path(tmp_path, C.ZETDIR, id_).mkdir(parents=True)

    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'clean', '--dry-run'])

    out, err = capsys.readouterr()
    assert (
        out == f"will delete {id_}\nUse '--force' to proceed with deletion\n"
    )
    assert err == ''
    assert Path(tmp_path, C.ZETDIR, id_).exists()


def test_clean_dry_run_and_force(tmp_path, capsys):
    id_ = '20211016205158'
    Path(tmp_path, C.ZETDIR, id_).mkdir(parents=True)

    main([*TEST_CFG, '--repo', tmp_path.as_posix(), 'clean', '-df'])

    out, err = capsys.readouterr()
    assert out == f'will delete {id_}\n'
    assert err == ''
    assert Path(tmp_path, C.ZETDIR, id_).exists()


def test_remote(tmp_path, capfd):
    init_dir = tmp_path.as_posix()
    main([*TEST_CFG, 'init', init_dir])
    # We're not interested in the 'pyzet init' output
    _, _ = capfd.readouterr()

    # Add remote, and then display it
    cmd = (*TEST_CFG, '-r', init_dir, 'remote', 'add', 'foo', 'zet-remote')
    main([*cmd])
    main([*TEST_CFG, '--repo', init_dir, 'remote'])

    out, err = capfd.readouterr()
    assert out == 'foo\n'
    assert err == ''
