# pyzet

[![Tests](https://github.com/wojdatto/pyzet/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/wojdatto/pyzet/actions/workflows/tests.yml)

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

You can read the more detailed tutorial
[here](https://github.com/wojdatto/pyzet/tree/main/docs).

## Configuration

A config file should be placed inside `~/.config/pyzet/pyzet.yaml`, and
looks like this:

```yaml
repo: ~/zet
editor: /usr/bin/vim
```

* `repo`: the location of the ZK Git repo

* `editor` (default: `/usr/bin/vim`): path to the editor used to add and
  edit zettels

### Support for multiple ZK repos

You can have multiple repos, and only a single config file, because
there is `--repo` flag that you can always set to point to a custom repo
(and possibly, create an alias that includes it). If `--repo` flag is
used, the value from YAML is ignored.

## Supported editors

Pyzet launches editor you defined in the config file with just
a positional argument of the zettel filename. It works fine with any
editor that doesn't require additional parameters to start (e.g., vim or
nano).

## Contributing

### Development installation

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

## Zettel formatting rules and guidelines

Zettels should use Markdown. It is preferred to use consistent flavor of
Markdown like [CommonMark](https://commonmark.org/). Pyzet will parse
zettel's content trying to extract information like title and tags.

In fact, many rules described below are derived from Rob Muhlestein's
ZettelMark specification that can be found
[here](https://github.com/rwxrob/zet/blob/main/20210812154738/README.md),
which is also based on CommonMark.

Some of the rules described below are only guidelines, but some of them
are needed for pyzet to correctly parse zettels.

### General formatting

For a convenient reading of zettels in the source form, it's recommended
to wrap lines. The [common standard](https://youtu.be/_U5heW26fvg) is to
break line after 72 characters.

Ideal zettels shouldn't be too long, and they should be a brief text
description of pretty much anything. Avoid pasting links in the zettel
core content and prefer using references section (described below) for
that.

Pyzet supports tagging zettels with hashtags for easier searching in the
future. For correct parsing, tags should all fit on a single line, so
their number is naturally limited. Ideally they should only use keywords
that are not a part of a zettel itself, so they can help obtaining
non-obvious connections. The tagging rules are described below.

Try to use consistent Markdown formatting. We recommend:

* Use only `*` for bold & italics

* Use only `*` for unordered lists

* If any item of an unordered lists take more than a single line,
  separate all of them with a single blank line

* Use `<>` to show that something is an URL. GitHub and VSCode will
  detect it even without it thanks to
  [GFM](https://github.github.com/gfm/#autolinks-extension-), but this
  is not true for every tool that supports Markdown (i.e. CommonMark
  doesn't support it).

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

* <http://example.com/>

* This is an example description\
  <http://described-example.com/>
```

ZettelMark doesn't specify a keyword for a reference block, but we like
`Refs` as it plays nice with `Tags` that will be described next.  At
this point, it's all up to the user preference.

If there is no URL description, an URL should be placed with a single
space between it and `*`.

If an URL have a description, it should go first. A Markdown syntax for
a hard line break (`\`) is used at the end of the description for a
better rendering in the HTML. Then, a link should start from a new line
preceded with two spaces, so it's aligned with the description.

Along with `\`, Markdown supports different syntax for hard breaks:

* two or more spaces
* inserting HTML `<br>` tag

We believe that `\` is superior to both of them, as a significant
trailing whitespace doesn't seem to be a right idea due to many reasons
(e.g. it's very well hidden from you while editing). Also, a good
practice is to avoid using plain HTML in Markdown files which eliminates
approach with `<br>`.

#### References shouldn't be wrapped

Even if a reference line is longer than 72 characters, ZettelMark tells
not to wrap lines in this section, probably for easier parsing. This
doesn't matter as long as `Refs` are not parsed by pyzet, but it seems
like a reasonable rule to follow, so we recommend it:

```markdown
Refs:

* <http://example.com/>

* This is an example of a a very long description for some very interesting link\
  <http://described-example.com/>

* This is an example of a slightly shorter description\
  <http://this-is-a-very-long-example-link-that-also-should-not-be-wrapped.com/>
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

Remember that tags line should end with a newline character, so the
caret is moved to the next line which should be empty. This is by
default assumed by some text editors like Vim, but is probably less
popular in Windows world.

There are different ways to guarantee that file ending is correct, and
one of them is using pre-commit with `end-of-file-fixer` hook that
[comes by default](https://github.com/pre-commit/pre-commit-hooks) with
that tool. It's very simple to setup pre-commit with ZK Git repository,
so we recommend it.

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
