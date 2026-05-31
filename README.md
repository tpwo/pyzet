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

* Python 3.10+
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

## Shell completion

`pyzet` supports tab completion. To enable it in your shell, add the following to your `.bashrc`, `.zshrc`, or equivalent shell configuration file:

    eval "$(register-python-argcomplete pyzet)"

## Configuration

A config file should be placed inside `~/.config/pyzet/pyzet.yaml`, and
looks like this:

```yaml
repo: ~/zet
editor: /usr/bin/vim
editor_args: []
```

* `repo`: the location of the ZK Git repo

* `editor`: use it to overwrite the default editor (by default we refer to
  `EDITOR` and `VISUAL` env variables)

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

## Development

> [!NOTE]
> `uv` is required for [justfile](justfile) commands to work correctly.

Prerequisites:

* [uv](https://github.com/astral-sh/uv) installed and on `PATH`
* [just](https://github.com/casey/just) installed and on `PATH`

### Installation and testing

Development dependencies are stored in `requirements-dev.txt`. [tox](https://github.com/tox-dev/tox) is used to specify test envs and how to install dependencies.

To install package in the editable mode with dev deps:

    just venv

To run pre-commit checks:

    just pre-commit

To run tests against all supported Python versions:

    just test

To measure code coverage:

    just coverage

To run all the above tests & checks:

    just all

### Building and releasing

To build a new version and verify it with `twine`:

    just build

> [!IMPORTANT]
> Make sure to generate an API token in PyPI.org in order to upload the new version.

To run all checks, build the package, and release it

    just release

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
