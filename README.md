# pyzet

[![Tests](https://github.com/tpwo/pyzet/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/tpwo/pyzet/actions/workflows/tests.yml)

> "I, of course, do not think everything by myself. It happens mainly
> within the Zettelkasten".

`pyzet` is a CLI tool targeted at note-taking and personal knowledge
management loosely inspired by the Zettelkasten approach, hence the
name. The whole workflow is centered around Git repos where notes are
stored.

## Installation

Prerequisites:

* Python 3.8+
* Git 2.25+ (but older also should be fine)

Unix and Windows are supported. You can install pyzet with pip:

    pip install pyzet

## Tutorial

For the quick setup for the either platform (make sure to create missing
folders):

    pyzet sample-config unix > ~/.config/pyzet/pyzet.yaml
    pyzet sample-config windows | Set-Content ~/.config/pyzet/pyzet.yaml

Run `pyzet init` to create Git repo.

You can read the more detailed tutorial in
[docs](https://github.com/tpwo/pyzet/blob/main/docs/tutorial.md).

## Configuration

A config file should be placed inside `~/.config/pyzet/pyzet.yaml`, and
looks like this:

```yaml
repo: ~/zet
editor: /usr/bin/vim
editor_args: []
```

* `repo`: the location of the ZK Git repo

* `editor` (default: `/usr/bin/vim`): path to the editor used to add and
  edit zettels

* `editor_args` (default: empty): optional list of CLI arguments which
  should be passed to the editor

### Support for multiple ZK repos

You can have multiple repos, and only a single config file, because
there is `--repo` flag that you can always set to point to a custom repo
(and possibly, create an alias that includes it). If `--repo` flag is
used, the value from YAML is ignored.

## Supported editors

See [docs](https://github.com/tpwo/pyzet/blob/main/docs/supported-editors.md).

## Writing parsable zettels

See [docs](https://github.com/tpwo/pyzet/blob/main/docs/zettel-formatting.md).

## Development installation

Development dependencies are stored in `requirements-dev.txt`. To
install the package in editable mode with the dev dependencies run the
following after cloning the repo:

    pip install -e .
    pip install -r requirements-dev.txt

For running tests more easily, you might also want to install `tox`:

    pip install tox

Then you can easily run:

    tox -e coverage    # pytest with test coverage
    tox -e pre-commit  # run pre-commit checks on all files

## Building

    tox                  # runs all tox envs making sure tests pass
    pyproject-build      # builds both the wheel and source dist
    twine check dist/*   # checks if the build isn't completely broken
    twine upload dist/*  # asks for username and password

It's best to use token (`__token__` as username) for the last command.

## Inspiration and further reading

[`@rwxrob`](https://github.com/rwxrob) inspired me to write a
stand-alone tool for note taking rather than use a ready solution. He
posted a good summary in [this video](https://youtu.be/26X2onaKGc0).

See also:

* Two essays by the creator of Zettelkasten, Niklas Luhmann\
  <https://luhmann.surge.sh/>

* Even simpler approach to Zettelkasten\
  <https://gsilvapt.me/posts/poor-man-zettel/>

* *Simple, Non-Commercial, Open Source Notes*, a great video about tools
  to do note-taking\
  <https://youtu.be/XRpHIa-2XCE>
