# FlakeLedger

![FlakeLedger wordmark, flake in slate and ledger in teal, with a mark showing one commit run twice with a failing and a passing attempt](docs/assets/logo.svg)

FlakeLedger reads JUnit XML result files from many CI runs, decides which
failing tests are flakes and which are genuine failures by comparing outcomes
across reruns of the same commit, then attributes a compute cost and a
developer wait cost to each flake and ranks them. The output is a report that
names specific tests worth fixing or deleting.

Python 3.11, standard library only. No third party dependencies, no network
access.

<div align="center">

**67.5008 USD of flaky test cost across the sample runs**

Charged to two tests, `test_apply_coupon` and `test_replica_catchup`, using the
default rates. Those rates are declared inputs you should replace with your own
measurements, not universal truths.

</div>

You probably recognise the situation the tool is built for. A pull request goes
red, someone re-runs the job, it goes green, and the change merges. Nobody
recorded that the first run failed or which test caused it, and the same test
will do it again next week to somebody else. The waste is real but spread across
many people and never added up. FlakeLedger adds it up from the XML your CI
already produces, so the argument for fixing a specific test stops being a
feeling and becomes a line in a ranked table.

## How it decides what is a flake

The unit of judgement is one test on one commit, across every rerun attempt of
that commit. Because the code does not change between reruns of the same commit,
a test that both passes and fails there cannot be blaming the code: something
other than the code under test decided the outcome, which is the operational
definition FlakeLedger uses.

The four labels, and the exact rule behind each:

| Label | Rule | Meaning |
|-------|------|---------|
| flake | passed on one attempt and failed on another, same commit | outcome depends on something other than the code |
| genuine_failure | every attempt failed, same commit | the failure reproduces, so it is real |
| stable | every attempt passed or skipped, no failure | nothing to act on |
| undetermined | failed on its only attempt for that commit | one observation, no rerun to compare against |

The comparison is always within a single commit. FlakeLedger never compares a
failure on commit A against a pass on commit B and calls the difference a flake,
because the code changed between those commits, so a differing outcome is
expected. Holding the commit constant is what makes the judgement sound, and the
design decisions section explains why that boundary is the unit.

## The undetermined case and why it refuses to guess

The hard case is a test that failed and was never re-run for that commit. With a
single observation there is no second attempt to compare against, so the data
cannot distinguish a flake from a genuine failure. A tool that guessed here
would be inventing a fact it does not have.

FlakeLedger refuses to guess. By default a single failing attempt is labelled
`undetermined`, and that label is a finding in its own right: it tells you the
data is insufficient, not that the test is fine. If you want a decision anyway,
you choose the rule explicitly with `--single-fail-policy`, and the chosen
policy is printed at the top of the output so the decision is never hidden:

| Policy value | Effect on a single failing attempt |
|--------------|------------------------------------|
| `undetermined` (default) | labelled undetermined, refuses to guess |
| `genuine` | labelled genuine_failure, a conservative flake hunt |
| `flake` | labelled flake, assumes a retry would have cleared it |

The default is `undetermined` on purpose. Silently counting one red run as a
flake would inflate the cost figure with tests that may be genuinely broken;
silently counting it as genuine would hide real flakes that were simply not
re-run. Neither silent choice is honest, so the honest default is to say the
data does not decide.

## Install

```
python -m pip install -e .
```

Or run without installing by putting the sources on the path:

```
set PYTHONPATH=src
python -m FlakeLedger version
