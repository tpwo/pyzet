# pyzet

A Python app that makes it easier to use Zettelkasten with git repos.

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
