# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

* Do not display binary files in `pyzet grep` output ([#18]).

## [0.2.0] - 2022-01-27

Introduce YAML config file, some new features, and bug fixes.

### Added

* Add support for YAML config file ([#13]).
* Add `pyzet init` command that creates a git repo ([#8]).
* Add quick start tutorial ([#12]).

### Changed

* Order CLI commands in a more intuitive way ([#11]).
* Add `--force` flag to `pyzet clean` ([#10]).

### Fixed

* Fix `pyzet rm` so it also removes other files in the zettel folder ([#9]).

## [0.1.0] - 2022-01-23

Initial release.

<!-- Links -->

[Unreleased]: https://github.com/wojdatto/pyzet/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.2.0
[0.1.0]: https://github.com/wojdatto/pyzet/releases/tag/v0.1.0

[#8]: https://github.com/wojdatto/pyzet/issues/8
[#9]: https://github.com/wojdatto/pyzet/issues/9
[#10]: https://github.com/wojdatto/pyzet/issues/10
[#11]: https://github.com/wojdatto/pyzet/issues/11
[#12]: https://github.com/wojdatto/pyzet/issues/12
[#13]: https://github.com/wojdatto/pyzet/issues/13
[#18]: https://github.com/wojdatto/pyzet/issues/18
