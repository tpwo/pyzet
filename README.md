# pyzet

[![Tests](https://github.com/wojdatto/pyzet/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/wojdatto/pyzet/actions/workflows/tests.yml)

A Python app that makes it easier to use Zettelkasten with git repos.

## How to use?

The current version is very limited in its capabilities. The basic
commands include listing, adding, editing, and removing zettels.

The default location of zet repo is `~/zet`. For now it's hard-coded
path that can be changed with `--repo` flag when executing any command.
In the future, a config file with option to alter the default path will
be added.

At this point, the editor for working with zettels is also hard-coded.
On Windows it's the default path to `vim.exe` that is installed with Git
for Windows. On Linux (and probably also on Mac), it is the default text
editor.

The option to change editor also will be included in the config file.

Summary of commands:

```none
$ pyzet -h
usage: pyzet [-h] [-V] [-r REPO] {status,list,tags,show,clean,add,edit,rm,grep,pull,push} ...

positional arguments:
  {status,list,tags,show,clean,add,edit,rm,grep,pull,push}
    status              run `git status` in zet repo,
                        use `--` before including git options
    list                list zettels in given repo
    tags                list tags in given repo
    show                print zettel contents
    clean               delete empty folders in zet repo
    add                 add a new zettel
    edit                edit a zettel
    rm                  remove a zettel
    grep                run `grep -rni` in zet repo
    pull                run `git pull --rebase` in zet repo
    push                run `git push` in zet repo,
                        use `--` before including git options

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -r REPO, --repo REPO  path to point to any zet repo
```

## How to run?

Python 3.7 or later is needed.

The app is still in early development. However, you can use `pip` to
install it directly from this repo:

```bash
pip install git+https://github.com/wojdatto/pyzet.git
pyzet --help
```

By default, `main` branch will be used. To use `develop` branch you need
to specify it:

```bash
pip install git+https://github.com/wojdatto/pyzet.git@develop
```

### Manual installation

Manual installation is also possible. Clone the repo and run the install
command. Using venv/virtualenv is advised.

```none
git clone https://github.com/wojdatto/pyzet.git
cd pyzet
```

Unix/Linux:

```bash
python3 -m venv venv
. venv/bin/activate # in bash `source` is an alias for `.`
pip install .
pyzet --help
```

Windows:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install .
pyzet --help
```

### Development installation

Development dependencies are stored in
[requirements-dev.txt](requirements-dev.txt). To install the package in
editable mode with the dev dependencies run the following after cloning
the repo:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Zettel formatting rules and guidelines

Zettels should use Markdown. It is preferred to use consistent flavor of
Markdown like [CommonMark](https://commonmark.org/). Pyzet will parse
zettel's contents trying to extract information like title and tags.

Some of the rules described below are only guidelines, but some of them
are needed for pyzet to correctly parse zettels.

### General formatting

For a convenient reading zettels in the source form, it's recommended to
wrap lines. The common standard is to break line after 72 characters.

Ideal zettels shouldn't be too long, and they should be a brief text
description of pretty much anything. Avoid pasting links in the zettel
core content and prefer using references section (described below) for
that.

Pyzet supports tagging zettels with hashtags for easier searching in the
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

Pyzet currently doesn't analyze references, but the suggested way to add
them is as follows:

```markdown
Refs:

* <http://described-example.com/> -- This is an example description
* <http://example.com/>
```

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

## TODO

* [ ] add a config file
* [ ] add integration with Git
* [ ] autocompletion for commands
* [ ] autocompletion for zettels (ID and title?)
* [ ] easier searching through zettels (maybe some interface to grep?)

## License

Unless explicitly stated otherwise all files in this repository are
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
