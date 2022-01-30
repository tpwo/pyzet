# pyzet

[![Tests](https://github.com/wojdatto/pyzet/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/wojdatto/pyzet/actions/workflows/tests.yml)

A small CLI tool that makes it easier to use Zettelkasten with git
repos.

## How to use?

The current version is limited in its capabilities, so it might be
frustrating to use. Don't hesitate to add an issue or PR, if you have
any idea how to improve or expand this tool, or you experienced any
problems. Any feedback is welcome!

The basic configuration of pyzet is set via YAML file which should be
placed at `~/.config/pyzet/pyzet.yaml`. However, there is a `--config`
flag that can be used to point to a custom config file using relative or
global path.

Config file contains four possible fields of which only `repo` is
required to be set. The remaining three will use default values if they
are not set in the config file.

### Default config values

On Linux (or actually "not Windows", so it will trigger also on Mac)
they will be compatible with Ubuntu and possibly some other distros:

    editor: /usr/bin/vim
    git: /usr/bin/git
    grep: /usr/bin/grep

On Windows the executables installed with Git for Windows are used as
default options:

    editor: C:/Program Files/Git/usr/bin/vim.exe
    git: C:/Program Files/Git/cmd/git.exe
    grep: C:/Program Files/Git/usr/bin/grep.exe

Forward slashes `/` can be used even on Windows. Backslashes `\` or
double backslashes `\\` should also work, but it wasn't thoroughly
tested.

Also, remember that paths cannot include env variables, but you can use
`~` to point to your `$HOME` directory.

For the sake of this readme, we assume that your repo setting will be
under `~/zet`.

You can have multiple repos, and only a single config file, because
there is `--repo` flag that you can always set to point to a custom repo
(and possibly, create an alias that includes it). If this flag is used,
the setting from YAML is ignored.

An example correct config file:

    repo: ~/zet
    editor: /usr/bin/vim
    git: /usr/bin/git
    grep: /usr/bin/grep

If you're on Linux, you can use the commands:

    mkdir -p ~/.config/pyzet
    pyzet sample-config > ~/.config/pyzet/pyzet.yaml

to create required folders and a copy of the above correct config file
into the default location.

## Quick start

Please see the tutorial
[here](https://github.com/wojdatto/pyzet/tree/main/docs).

## Summary of commands

```none
$ pyzet -h
usage: pyzet [-h] [-r REPO] [-c CONFIG] [-V] {init,add,edit,rm,show,list,tags,clean,grep,status,pull,push,sample-config} ...

positional arguments:
  {init,add,edit,rm,show,list,tags,clean,grep,status,pull,push,sample-config}
    init                initialize a git ZK repository
    add                 add a new zettel
    edit                edit a zettel
    rm                  remove a zettel
    show                print zettel contents
    list                list zettels in given repo
    tags                list tags in given repo
    clean               delete empty folders in zet repo
    grep                run `grep -rniI` in zet repo
    status              run `git status` in zet repo
    pull                run `git pull --rebase` in zet repo
    push                run `git push` in zet repo
    sample-config       Produce a sample pyzet.yaml file

options:
  -h, --help            show this help message and exit
  -r REPO, --repo REPO  path to point to any zet repo
  -c CONFIG, --config CONFIG
                        path to alternate config file
  -V, --version         show program's version number and exit
```

## Supported editors

pyzet is a CLI application which cooperates with a text editor of
choice. The best integration can be probably achieved when also using a
CLI text editor.

But this is not necessary. Currently, pyzet can cooperate with different
text editors, even these that have a GUI but the integration is not
ideal.

Below are listed editors that pyzet was tested with. To use a given
editor, add an `editor` field to your config file.

### Linux

The actual testing was done on Ubuntu WSL2 with these CLI editors, and
they work fine:

    editor: vim
    editor: nano

### Windows

On Windows, the following editors seem to work fine:

    editor: vim  # only if running pyzet from Git Bash
    editor: nano # only if running pyzet from Git Bash
    editor: C:/Program Files/Git/usr/bin/vim.exe
    editor: C:/Program Files/Git/usr/bin/nano.exe
    editor: C:/Program Files/Windows NT/Accessories/wordpad.exe
    editor: notepad.exe

Some issues were found with:

Notepad++ -- closing a tab is not enough, you have to close the whole
program to save a zettel.

    editor: C:/Program Files/Notepad++/notepad++.exe

VS Code -- issues with adding a zettel. If zettel file already exists,
then it seems to work similarly to Notepad++ (you have to close the
whole program to save a zettel):

    editor: C:/Program Files/Microsoft VS Code/Code.exe

## How to run?

Python 3.7 or later is needed.

The simplest way to install is to use pip:

    pip install pyzet
    pyzet --help

You can also obtain the newest version from the `develop` branch
directly from this repository:

    pip install git+https://github.com/wojdatto/pyzet.git@develop

### OS compatibility

Both Windows and Unix are supported, but the current version is 5-10
times faster with the latter. One of the reasons of worse performance
might be Windows Defender with its realtime protection.

On of the workarounds is trying to use pyzet with
[WSL2](https://docs.microsoft.com/en-us/windows/wsl/install).

### Manual installation

Manual installation is also possible. Clone the repo and run the install
command. Using virtual environment is advised.

    git clone https://github.com/wojdatto/pyzet.git
    cd pyzet

Unix/Linux:

    python3 -m venv venv
    . venv/bin/activate # in bash `source` is an alias for `.`
    pip install .
    pyzet --help

Windows:

    python -m venv venv
    .\venv\Scripts\activate
    pip install .
    pyzet --help

### Development installation

Development dependencies are stored in
[requirements-dev.txt](requirements-dev.txt). To install the package in
editable mode with the dev dependencies run the following after cloning
the repo:

    pip install -e .
    pip install -r requirements-dev.txt

### Running automatic tests

pyzet uses pytest and tox to run automatic tests. Use `pytest` command
to test against the current Python version, or use `tox` to test against
all supported Python versions (you, of course, have to install them
first). [Pre-commit](https://pre-commit.com/) is also configured as one
of tox's envs.

Automatic test coverage is not ideal at this point, and some commands
are only tested manually.

## Zettel formatting rules and guidelines

Zettels should use Markdown. It is preferred to use consistent flavor of
Markdown like [CommonMark](https://commonmark.org/). pyzet will parse
zettel's content trying to extract information like title and tags.

In fact, many rules described below are derived from rwxrob's ZettelMark
specification that can be found
[here](https://github.com/rwxrob/zet/blob/main/20210812154738/README.md),
which is also based on CommonMark.

Some of the rules described below are only guidelines, but some of them
are needed for pyzet to correctly parse zettels.

### General formatting

For a convenient reading zettels in the source form, it's recommended to
wrap lines. The common standard is to break line after 72 characters.

Ideal zettels shouldn't be too long, and they should be a brief text
description of pretty much anything. Avoid pasting links in the zettel
core content and prefer using references section (described below) for
that.

pyzet supports tagging zettels with hashtags for easier searching in the
future. The number of tags shouldn't be too big, and ideally they should
only use keywords that are not a part of a zettel itself. The tagging
rules are described below.

Try to use consistent Markdown formatting. We recommend:

* Use only `*` for bold & italics

* Use only `*` for unordered lists

* If items of unordered lists take more than a single line (will happen
  if you wrap after 72 chars), separate them with a single blank line

* Use `<>` to show that something is a link. GitHub and VSCode will
  detect it even without it, but this is not true for every tool that
  supports Markdown

### Title line

The first line of a zettel that should start with `#` and a single
space, and then the title itself. Title line shouldn't have any leading
or trailing spaces.

If wrong formatting is detected, a warning will be raised and pyzet will
show you a raw title line instead of a parsed one.

Ideally, title should not exceed 50 characters. This is because a title
is also a commit message in a Zettelkasten repo, and GitHub will snip
messages longer than 50 characters when displaying commit messages next
to the files. At this point, this is not checked by pyzet, so no warning
will be raised in that case.

```markdown
# Example correct zettel title
```

### References

pyzet currently doesn't analyze references, but the suggested way to add
them is as follows:

```markdown
Refs:

* <http://described-example.com/> -- This is an example description
* <http://example.com/>
```

`--` is used here as poor man's [En
dash](https://en.wikipedia.org/wiki/Dash#En_dash) as it's not available
directly from ASCII. However, this won't matter as long as `Refs` are
not parsed by pyzet.

If description is longer, break line after 72 characters and put a blank
line between references:

```markdown
Refs:

* <http://described-example.com/> -- This is an example of a longer
  description

* <http://example.com/>
```

### Tags

Tags are optional, but if they're used, they should be placed as the
last line of a zettel that starts from 4 or more leading spaces (it's
Markdown syntax for a fenced code block that renders as monospaced
font). Each tag should start with `#` and should be separated with a
single space from the next one.

Using small letters and `kebab-case` is recommended as a consistent
tagging style, but it's not forced or checked at this moment. A tag line
can be preceded by `Tags:` and a single blank line to make zettels more
structured.

```markdown
Tags:

    #tag1 #tag2 #another-tag
```

## Inspiration and further reading

The biggest inspiration for this project was
[`@rwxrob`](https://github.com/rwxrob), and his approach to
Zettelkasten. Probably the best way to get a grasp of it, is to read
about it in [his public Zettelkasten
repo](https://github.com/rwxrob/zet/blob/main/README.md). Rob also
maintains a Bash CLI tool
[`cmd-zet`](https://github.com/rwxrob/cmd-zet.git).

See also:

* <https://luhmann.surge.sh/> -- two essays by the creator of
  Zettelkasten, Niklas Luhmann

* <https://gsilvapt.me/posts/building-a-zettelkasten-the-simple-way/> --
  even simpler approach to Zettelkasten

* <https://github.com/gsilvapt/pmz.git> -- similar tool written in Go

* <https://github.com/Zettlr/Zettlr.git> -- if you cannot live without a
  GUI, this might be an alternative tool for you. There is also an
  [interesting video](https://youtu.be/c5Tst3-zcWI) from the author of
  this tool that describes his vision of Zettelkasten.

## License

Unless explicitly stated otherwise, all files in this repository are
licensed under the Apache Software License 2.0:

> Copyright 2021 Tomasz Wojdat
>
> Licensed under the Apache License, Version 2.0 (the "License"); you
> may not use this file except in compliance with the License. You may
> obtain a copy of the License at
>
>     http://www.apache.org/licenses/LICENSE-2.0
>
> Unless required by applicable law or agreed to in writing, software
> distributed under the License is distributed on an "AS IS" BASIS,
> WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
> implied. See the License for the specific language governing
> permissions and limitations under the License.
