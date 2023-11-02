# pyzet

[![Tests](https://github.com/tpwo/pyzet/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/tpwo/pyzet/actions/workflows/tests.yml)

> "I, of course, do not think everything by myself. It happens mainly
> within the Zettelkasten".

`pyzet` is a CLI tool targeted at note-taking and personal knowledge
management using the Zettelkasten approach with Git repos.

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

## Inspiration and further reading

The biggest inspiration for this project was Rob Muhlestein
([`@rwxrob`](https://github.com/rwxrob)), and his approach to
Zettelkasten. Probably the best way to get a grasp of it, is to read
about it in [his public Zettelkasten
repo](https://github.com/rwxrob/zet/blob/main/README.md). Rob also
maintains a Bash CLI tool
[`cmd-zet`](https://github.com/rwxrob/cmd-zet).

See also:

* Two essays by the creator of Zettelkasten, Niklas Luhmann\
  <https://luhmann.surge.sh/>

* Even simpler approach to Zettelkasten\
  <https://gsilvapt.me/posts/building-a-zettelkasten-the-simple-way/>

* Similar tool written in Go by the author of the above\
  <https://github.com/gsilvapt/pmz>

* A Zettelkasten tool for people who prefer to have a GUI\
  <https://github.com/Zettlr/Zettlr>

  There is also an [interesting video](https://youtu.be/c5Tst3-zcWI)
  from the author of this tool that describes his vision of
  Zettelkasten.
