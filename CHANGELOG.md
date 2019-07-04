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
