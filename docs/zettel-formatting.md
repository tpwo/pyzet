# Zettel formatting rules and guidelines

Zettels should use Markdown. It is preferred to use consistent flavor of
Markdown like [CommonMark](https://commonmark.org/). Pyzet will parse
zettel's content trying to extract information like title and tags.

In fact, many rules described below are derived from Rob Muhlestein's
ZettelMark specification that can be found
[in this zettel](https://github.com/rwxrob/zet/blob/11285028bc4f8b2cd0ed35e852dc580e9e74a104/20210812154738/README.md),
which is also based on CommonMark.

Some of the rules described below are only guidelines, but some of them
are needed for pyzet to correctly parse zettels.

## General formatting

For a convenient reading of zettels in the source form, it's recommended
to decide on whether to wrap lines or not in your zet repo. The case for
wrapping during writing is similar to writing Git commit messages, and
[here is an
explanation](https://github.com/torvalds/linux/pull/17#issuecomment-5661185)
of the reasons. But you can decide not to wrap the lines at all, and
always rely on automatic text wrapping when they're displayed which is
handled very well in case of Markdown.

Ideal zettels shouldn't be too long, and they should be a brief text
description of pretty much anything. Avoid pasting links in the zettel
core content and prefer using references section (described below) for
that.

Pyzet supports tagging zettels for easier searching in the future. For
correct parsing, tags should all fit on a single line, so their number
is naturally limited. Ideally they should only use keywords that are not
a part of a zettel itself, so they can help obtaining non-obvious
connections. The tagging rules are described below.

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

## Title line

The first line of a zettel that should start with `#` and a single
space, and then the title itself. Title line shouldn't have any leading
or trailing spaces.

If wrong formatting is detected, a warning will be raised and pyzet will
show you a raw title line instead of a parsed one.

```markdown
# Example correct zettel title
```

## References

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

### References shouldn't be wrapped

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

## Tags

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
