# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2023-02-12

### Added

* Auto-squash commits after multiple edits to the same zettel in a row
  (#51)

### Changed

* Include `-v` flag in `pyzet remote` by default (#48).

### Removed

* Get rid of `git` config field, and just use Git from PATH (#53).

## [0.6.0] - 2022-04-18

### Added

* Add pyzet remote command (#41).
* Allow for changing the initial branch name in `pyzet init` (#42).

### Changed

* Reorganization & update of the readme and tutorial (#36).
* Update URL formatting suggested in the docs (#30).
* Simplify zettel relative links by removing `--` from them (#31).
* Extend `pyzet sample-config` to provide sane defaults also for Windows
  (#38).

### Fixed

* Fix `pyzet init` when a custom target path was provided (#40).

## [0.5.0] - 2022-04-04

### Added

* Add `--verbose` flag to control logging level (#28).

### Changed

* Use `print()` for all standard program output, and `logging` for
  displaying additional information. Logging level was changed to
  `WARNING`, so existing warnings will be showed by default.
* Switch to use single quotes over back quotes in the program output.
* Remove implicit `--ignore-case` option from `pyzet grep`; the flag
  with this name was created and it should be explicitly added to
  maintain the old behavior (#29).

## [0.4.0] - 2022-04-03

### Added

* Add `--link` flag to `pyzet list` and `pyzet show` (#21).
* Add `--line-number` flag to `pyzet grep` which was previously applied
  automatically (#23).
* Add `--title` flag to `pyzet grep` which shows the title of matched
  zettel (#24).
* Allow for passing multiple patterns in `pyzet grep` (#25).
* Allow for passing custom options in `pyzet grep` (#27).

### Changed

* Use `--` in `pyzet list` and `pyzet list --pretty` output. Before, a
  single dash was used. The new syntax is in line with recommendations
  about including references in zettels that can be found in the readme.
  It's also used in `pyzet list --link` and `pyzet show --link` output.
* Make output of `pyzet grep` more readable by using `--heading` and
  `--break` flags in `git grep` that is called by this command (#23).

## [0.3.0] - 2022-02-18

Start using `git grep` rather than relying on availability of `grep`
executable which means even simpler config file.

### Changed

* Do not display binary files in `pyzet grep` output (#18).
* Use `git grep` over `grep` (#18).

## [0.2.0] - 2022-01-27

Introduce YAML config file, some new features, and bug fixes.

### Added

* Add support for YAML config file (#13).
* Add `pyzet init` command that creates a git repo (#8).
* Add quick start tutorial (#12).

### Changed

* Order CLI commands in a more intuitive way (#11).
* Add `--force` flag to `pyzet clean` (#10).

### Fixed

* Fix `pyzet rm` so it also removes other files in the zettel folder
  (#9).

## [0.1.0] - 2022-01-23

Initial release.

<!-- Links -->

[Unreleased]: https://github.com/wojdatto/pyzet/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.7.0
[0.6.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.6.0
[0.5.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.5.0
[0.4.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.4.0
[0.3.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.3.0
[0.2.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.2.0
[0.1.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.1.0
