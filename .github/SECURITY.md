# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.5.x   | yes       |
| < 0.5   | no        |

## Reporting a vulnerability

FlakeLedger parses CI artefacts offline, so the attack surface is narrow but
real:

- unbounded memory on crafted JUnit XML (nested suites, huge attributes),
- quadratic regex/parse behaviour on adversarial timestamps,
- report injection: case names from results must be escaped so a crafted
  suite name cannot smuggle markup into the rendered ledger or JSON.

Please do **not** open a public issue for these. Contact the repository owner
through the profile with:

1. The affected version (`flakeledger version` or the commit SHA).
2. The smallest JUnit XML that triggers the behaviour.
3. Expected vs. actual behaviour.

You will get an acknowledgement within a week. Fixes land in the next minor
release and the reporter is credited in the changelog unless they prefer
otherwise.

## Scope

- `junit.py` - untrusted input, primary focus.
- `runs.py` / `classify.py` - grouping and pairing logic.
- `report.py` - escaping of result-derived strings in output.
