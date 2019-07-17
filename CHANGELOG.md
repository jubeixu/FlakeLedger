# Changelog

All notable changes to this project are documented here.

## [Unreleased]

## [0.5.0] - 2026-08-05

### Added
- `report` ranks flakes by combined compute + developer-wait cost and names
  the tests worth fixing or deleting.
- `docs/assets/flake-tax.svg`: the flake taxonomy diagram.
- Sample runs extended to six attempts across three commits.

### Changed
- Cost model rates are declared inputs with documented defaults, not
  hard-coded constants.

## [0.4.0] - 2024-07-30

### Added
- `cost` module: per-flake compute seconds and developer wait minutes.
- Undetermined classification for cases with too few attempts.

### Changed
- JUnit reader accepts property-entry run identity as well as suite
  attributes; malformed XML now raises a typed error instead of KeyError.

## [0.3.0] - 2022-11-02

### Added
- Attempt pairing by commit: reruns of the same commit are matched even when
  job ids differ.
- `classify` distinguishes flakes from genuine failures across reruns.

## [0.2.0] - 2021-03-19

### Added
- `runs` grouping: per-test outcome tables across runs of one commit.
