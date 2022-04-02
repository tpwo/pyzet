# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* Add `--link` flag to `pyzet list` and `pyzet show` (#21).

### Changed

* Use `--` in `pyzet list` and `pyzet list --pretty` output. Before, a
  single dash was used. The new syntax is in line with recommendations
  about including references in zettels that can be found in the readme.
  It's also used in `pyzet list --link` and `pyzet show --link` output.

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

[Unreleased]: https://github.com/wojdatto/pyzet/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.3.0
[0.2.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.2.0
[0.1.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.1.0
