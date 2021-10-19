# pyzet

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
usage: pyzet [-h] [-V] [-r REPO] {list,show,clean,add,edit,rm} ...

positional arguments:
  {list,show,clean,add,edit,rm}
    list                list zettels in given repo
    show                print zettel contents
    clean               delete empty folders in zet repo
    add                 add a new zettel
    edit                edit a zettel
    rm                  remove a zettel

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -r REPO, --repo REPO  path to point to any zet repo
```

## How to run?

Python 3.7 or later is needed.

The app is still in early development. However, you can use `pip` to
install it directly from this repo:

```bash
pip install git+https://github.com/trivvz/pyzet.git
pyzet --help
```

By default, `main` branch will be used. To use `develop` branch you need
to specify it:

```bash
pip install git+https://github.com/trivvz/pyzet.git@develop
```

### Manual installation

Manual installation is also possible. Clone the repo and run the install
command. Using venv/virtualenv is advised.

```none
git clone https://github.com/trivvz/pyzet.git
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
