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
```

That prints `FlakeLedger 0.1.0` and exits clean.

## Commands

| Command | What it does |
|---------|--------------|
| `ingest` | parse JUnit XML and list every case result, one per line |
| `classify` | label each test on each commit as flake, genuine, stable, undetermined |
| `cost` | rank flaky tests by attributed cost using explicit rates |
| `version` | print the version and exit |

Run identity is read from each `testsuite`, either as `commit` and `attempt`
attributes or as `<property>` entries. Point any command at files or at a
directory of `*.xml`. A directory expands to its `*.xml` files, sorted by name;
a file is used as itself. Nonexistent paths are ignored, and if the whole input
set resolves to no XML files the command exits with a usage error rather than
crashing on a missing file.

`classify` and `cost` also accept `--single-fail-policy`. `cost` additionally
accepts the three rate flags and a `--currency` label described next.

## The cost model

Every rate is an input, not a fact. The defaults exist so a run produces
numbers, but they are placeholders for values you should measure yourself.
Nothing here is a universal truth.

| Rate flag | Default | Unit | What it means |
|-----------|---------|------|---------------|
| `--compute-rate-per-minute` | 0.008 | currency per compute minute | money cost of one CI compute minute |
| `--dev-rate-per-minute` | 1.50 | currency per developer minute | money cost of one developer minute |
| `--dev-wait-minutes-per-flaky-event` | 15.0 | developer minutes per event | time one flaky event burns while someone waits on and re-triggers a red pipeline |
| `--currency` | USD | label only | text printed next to figures, no conversion |

How to get real values: divide a CI invoice by the compute minutes it billed for
the compute rate, use a loaded engineering cost per minute for the developer
rate, and estimate the wait minutes from how long your team loses to one red
pipeline. All three are knobs; change them and every figure moves, because
nothing is hardcoded inside the formula.

Wasted compute is the flaky test's own mean runtime times the rerun attempts
beyond the first, summed over every commit where it flaked, then valued at the
compute rate. Developer wait cost is `dev-wait-minutes-per-flaky-event` minutes
per flaky event valued at the developer rate, where a flaky event is one commit
the test flaked on (two commits means two events).

The compute figure is a deliberate lower bound. It counts only the flaky test's
own runtime. In real CI a flake usually forces a rerun of a whole job, so the
true compute waste is larger than reported. FlakeLedger will not guess job
composition, because that information is not in the JUnit data, so it attributes
only the part it can measure and states plainly that the real number is higher.

## A worked run over the samples

The `samples/` directory holds hand authored JUnit fixtures spanning four
commits with reruns. The three stages below are a single run of the pipeline
over those files, ingest to classify to cost, captured verbatim.
