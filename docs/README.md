# Quick start with pyzet

## Disclaimer for Windows users

This instruction is written with a Linux user in mind. If you're on
Windows, and you don't want to use WSL2, you can still follow it, but it
will be much easier, if you do it using Git Bash that comes with Git for
Windows. With that, all commands will be very similar, and the main
difference will be the location of your home folder. On Linux, it's by
default:

    $ echo $HOME
    /home/<your-username>

And on Git Bash it will be shown as:

    $ echo $HOME
    /c/Users/<your-username>

which is very Git Bash specific and won't work if put it in the config
file.

Generally, in your config file you can use Windows-like path, but we
suggest to use forward slashes `/` rather than backslashes `\` or double
backslashes `\\`, because it wasn't thoroughly tested.

Home directory written with this is mind should look like this:

    C:/Users/<your-username>

## Installation

Install pyzet using one of the methods described in the main readme,
e.g.:

    pip install pyzet

Now, run `pyzet` command to see if it is installed correctly. You should
see a usage hint:

    $ pyzet
    usage: pyzet [-h] <here will a list of flags and available commands>

For more detailed information, you can always use `--help` flag: `pyzet
-h`.

## Initial configuration

Let's start by initializing our zettelkasten repository:

    $ pyzet init
    ERROR: config file at `/home/<your-username>/.config/pyzet/pyzet.yaml` not found.
    Add it or use `--config` flag.

Whoops! If you saw a similar error, it means that you also don't have a
config file at this moment.

Let's create the simplest config file possible at
`~/.config/pyzet/pyzet.yaml` that will contain only a single line:

    repo: ~/zet

You can quickly do it with these two commands:

    mkdir -p ~/.config/pyzet
    echo 'repo: ~/zet' > ~/.config/pyzet/pyzet.yaml

Now, it should work:

    $ pyzet init
    Initialized empty Git repository in /home/<your-username>/zet/.git/
    INFO:root:Git repo was initialized. Please add a remote manually.

## Zettelkasten with Git

The idea behind pyzet is that each ZK repository is also a git
repository to have ZK history under control. It also opens an ability to
easily backup it to any Git hosting of your choice. Adding a remote
needs to be done manually, so you have to know the basics of Git, and
have it set up correctly (at the beginning, setting [commit name and
email](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup)
will be enough).

For the sake of this tutorial, let's ignore a prompt to add a remote for
our newly created Git repo. However, you'd probably like to do this in
your standard pyzet workflow. Probably, a good idea is to create a
private `zet` repository on any online Git hosting of your choice.

## Basic interaction with zettels

Now, you can proceed with adding your first zettel with `pyzet add`. The
text editor should open. Let's add some example text using
[Markdown](https://commonmark.org/):

```markdown
# This is my first zettel created with pyzet

The above line is the title of this zettel, and this is part of
its contents. It's a good practice to wrap lines like that, so zettels
are easier to read in the terminal.

Refs:

* <https://github.com/wojdatto/pyzet> -- this way you can add links

Tags:

    #tutorial
```

Save the file and exit from your editor. You should see a similar
output:

    $ pyzet add
    INFO:root:20220126232605 was created
    [main (root-commit) 7d40260] This is my first zettel created with pyzet
    1 file changed, 14 insertions(+)
    create mode 100644 zettels/20220126232605/README.md

Now, you can run `pyzet show` to see your zettel:

    $ pyzet show
    ============================ 20220126232605 ============================
    # This is my first zettel created with pyzet

    The above line is the title of this zettel, and this is part of
    its contents. It's a good practice to wrap lines like that, so zettels
    are easier to read in the terminal.

    Refs:

    * <https://github.com/wojdatto/pyzet> -- this way you can add links

    Tags:

        #tutorial

If you made a typo, you can edit your zettel with `pyzet edit` command.

Now, let's make a second zettel with `pyzet add`:

```markdown
# This is my second zettel

A short one :D

Tags:

    #tutorial #example-tag
```

Again, you can show it with `pyzet show`:

    $ pyzet show
    ============================ 20220123233028 ============================
    # This is my second zettel

    A short one :D

    Tags:

        #tutorial #example-tag

You might ask, "well, how can I show the first zettel now?". The
behavior of `pyzet show` is simple: by default it shows the zettel with
the highest ID (i.e. the latest one). To see older zettels, you have to
provide an ID.

But how can you obtain the ID of the first zettel? It's a pretty long
number, right?

The simplest way is to show a list of all zettels, and copy it. You can
do it with `pyzet list`:

    $ pyzet list
    20220126232605 - This is my first zettel created with pyzet
    20220126232716 - This is my second zettel

BTW, these numbers are not random. They actually follow special
timestamp format that consists of the current year, month, day, hour,
minute, and second in this very exact order. The hour, though, will most
likely not match your local time. This is done on purpose -- we use
UTC+0 to make sure that each ID is unique (at least, as long as you
don't try to create multiple zettels at the same second :p)

You can see that my ID of the first zettel was `20220126232605`. I can
now paste it to the `show` command:

    $ pyzet show 20220126232605
    ============================ 20220126232605 ============================
    # This is my first zettel created with pyzet
    <snip>

I mentioned that you can edit a zettel with `pyzet edit` command. As you
might guess, it also works with the last zettel by default, and you need
to provide an ID to edit an older zettel.

## Rage quit option

If you ever mess up during the editing of your zettel or you would like
to cancel adding of the new zettel, there is always a way to withdraw --
just remove *everything* from a zettel. This aborts the adding/editing
process making no actual changes on the drive, and it the git repo.

## Tags

As you might saw, we added some tags in our zettels. There is a `pyzet
tags` command that allows you to interact with them:

    $ pyzet tags
    1       #example-tag
    2       #tutorial

The number shows how many times each tag was used in your zettelkasten
repository. You can use it to maintain more coherent tag naming over
time. There are also some additional options, you can see them with
`pyzet tags -h` (and this is true for almost every command, BTW).

## Removing zettels

There is also `pyzet rm` command that allows you to remove a zettel.
It's a bit different: you have to provide the ID each time, even for the
newest zettel, e.g. to remove my second zettel I should run the
following:

    $ pyzet rm 20220126232716
    20220126232716 will be deleted including all files that might be inside. Are you sure? (y/N): y
    INFO:root:/home/<your-username>/zet/zettels/20220126232716/README.md was removed
    [main 009b935] RM: This is my second zettel
    1 file changed, 7 deletions(-)
    delete mode 100644 zettels/20220126232716/README.md
    INFO:root:/home/<your-username>/zet/zettels/20220126232716 was removed

As you can see, I had to confirm the deletion with `y` (capitalization
matters). Pressing `Enter` or any other key will abort the process.

Because pyzet uses Git, the removed zettel is still available in the Git
history. In order to completely remove it, you need to purge it
completely from the Git history which means that you need to rewrite it
(i.e. remove any commit that involved adding/editing such zettel, and
rebase commits that happened later.)

## Git remote interaction

pyzet ships with a few commands that make it easier to interact with a
Git remote. However, the work is always done by Git executable itself --
pyzet just calls it with the correct parameters.

The simplest command is `pyzet status` -- it just runs `git status` in
your ZK repo:

    $ pyzet status
    On branch main
    nothing to commit, working tree clean

For the remaining Git-interaction commands, you have to make sure that
your Git configuration including name, email, and remote is correct.

Once you're ready, you can try out these commands:

* `pyzet pull` -- runs `git pull` in your ZK repo
* `pyzet push` -- runs `git push` in your ZK repo

Also, for `status`, and `push` commands you can pass flags that will go
directly to Git. However, the syntax is a bit weird, because you have to
use `--` before supplying Git options. E.g. to make a force push you
have to:

    pyzet push -- -f

Overall, Git integration is very simple, because pyzet don't want to
complicate Git related stuff more than it's needed. We think that one
branch is enough, and for more sophisticated Git-related work you can
just `cd ~/zet`, and run Git commands directly.

## Search for anything using grep

Grep is your friend when you try to look for something in your ZK repo,
especially when it has grown a bit. `pyzet grep` command works by
running grep with these flags:

* `-r` -- it makes a search recursive, meaning that grep will visit
  every zettel, and print a line from it if it matches search criteria.

* `-n` -- it adds a line number to the grep output, so you know where
  the match occurred.

* `-i` -- it tells grep to ignore letter case.

* `-I` -- it tells grep to ignore binary files.

Grep is run directly in `zettels` folder in your ZK repo. If you happen
to have different files in there, it will also check them, so remember
about it.

Now, run a grep search on our repo, as we have one zettel in there.
Let's use `zettel` as a search pattern:

    $ pz grep zettel
    /home/<your-username>/zet/zettels/20220126232605/README.md:1:# This is my first zettel created with pyzet
    /home/<your-username>/zet/zettels/20220126232605/README.md:3:The above line is the title of this zettel, and this is part of
    /home/<your-username>/zet/zettels/20220126232605/README.md:4:its contents. It's a good practice to wrap lines like that, so zettels

As you can see, we've got three matches. In your output, you should also
see some nice coloring (e.g. matched pattern colored with red) if only
your terminal configuration supports it.

## Clean command

The last command to go through is `pyzet clean`. It works a bit
similarly to `git clean` but targets a very specific use case: it
removes empty folders at your ZK repo.

Let's try it. At first, let's create an empty folder with `mkdir
~/zet/zettels/test`. Now, we can run the command:

    $ pyzet clean
    will delete test
    Use `--force` to proceed with deletion

Let's do as asked:

    $ pyzet clean --force
    deleting test

And the folder was removed. If you ever happen to have an empty folder
that matches the timestamp syntax used by pyzet, `pyzet list` output
will show a warning about it. We can simulate it:

Let's remove `REAMDE.md` from our only zettel:

    rm ~/zet/zettels/20220126232605/README.md

And now, list the zettels:

    $ pyzet list
    WARNING:root:empty zet folder 20220126232605 detected
    ERROR: there are no zettels at given repo.

Now you can just run `pyzet clean --force` to get rid of this warning.

## Summary

This concludes the tutorial. It should give you a basic idea how to use
pyzet, and create your own ZK repository with it.

If you're new to the zettelkasten, it might be helpful to read more
about it. I suggest to go through `Inspiration and further reading`
section in the main readme.

If you have any questions or suggestions, feel free to create an issue
or pull request.
