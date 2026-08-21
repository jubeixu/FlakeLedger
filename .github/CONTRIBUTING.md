# Contributing to FlakeLedger

Thanks for helping put a price on flaky tests. Ground rules first.

## Ground rules

- **Standard library only.** `flakeledger` runs on Python 3.11 with zero
  third-party dependencies and zero network access. There has never been a
  dependency good enough to break this rule.
- **Deterministic reports.** The same JUnit inputs must produce a
  byte-identical ledger. No wall-clock, no dict iteration order, no locale
  formatting.
- **Rates are inputs, not opinions.** Cost rates live in configuration with
  documented defaults. Never hard-code a new rate.

## Workflow

1. Branch from `main` (`feat/<topic>` or `fix/<topic>`).
2. One behaviour per PR - small and reviewable.
3. Check locally:
   ```bash
   pip install -e .
   pytest
   python -m flakeledger ingest samples/*.xml
   ```
4. Open the PR describing *why*, not just *what*.

## Adding a JUnit dialect

The reader (`junit.py`) handles suite-attribute and property-entry run
identity. New dialects need:

- a fixture in `samples/` (synthetic, no real job ids or hostnames),
- round-trip tests in `tests/test_junit.py`,
- a note in `docs/` on how the identity is read.

## Reporting issues

Use the bug template and attach the JUnit XML that mis-parses. Synthetic
suitenames are fine - the case names in `samples/` show the level of detail
needed to reproduce most classification bugs.

## Code style

- `pytest -q` stays green; golden outputs guard the rendered ledger.
- Public JSON keys in the report are schema-stable and never renamed without
  a major version.
