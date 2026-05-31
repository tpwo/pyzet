# print this help message
help:
	just -l

# create venv and install package in editable mode
venv: _tox
	tox devenv

# run all checks and tests
all: pre-commit test coverage

# run pre-commit
pre-commit: _tox
	tox run -e pre-commit

# run tests against all supported python versions
test: _tox
	tox run

# run tests and measure code coverage
coverage: _tox
	tox run -e coverage

_tox:
	uv tool install tox --with tox-uv

# release python package to pypi.org
release: all build
	twine upload dist/*

# build python package
build:
	rm -rf dist
	uv tool install build
	pyproject-build
	uv tool install twine
	twine check dist/*
