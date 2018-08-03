"""Classify each test on each commit as a flake, a genuine failure, or stable.

Definitions used here, stated so the label is auditable:

  FLAKE
    The same test, on the same commit, both passed and failed across its
    reruns. The code did not change between attempts, so a differing outcome
    means the test result depends on something other than the code. That is
    the operational definition of a flaky test.

  GENUINE_FAILURE
    Every attempt of the test on that commit failed. The failure reproduces,
    so it is attributable to the code or the test, not to nondeterminism.

  STABLE
    Every attempt passed (or was skipped with at least one pass and no
    failure). Nothing to act on.

  UNDETERMINED
    Only one attempt exists for that commit and it failed. With a single
    observation we cannot distinguish a flake from a genuine failure: a
    rerun never happened. We refuse to guess. The explicit rule for this
    ambiguous case is configurable and defaults to UNDETERMINED so a single
    red run is never silently counted as either category. Callers who want a
    conservative flake hunt can set the policy to treat it as GENUINE_FAILURE,
    and callers who assume retries would have cleared it can set FLAKE. The
    chosen policy is recorded in the output.
"""

from __future__ import annotations

from dataclasses import dataclass

from flakeledger.runs import TestOnCommit

FLAKE = "flake"
GENUINE_FAILURE = "genuine_failure"
STABLE = "stable"
UNDETERMINED = "undetermined"

# Policies for the single-attempt-failed ambiguous case.
SINGLE_FAIL_UNDETERMINED = "undetermined"
SINGLE_FAIL_GENUINE = "genuine"
SINGLE_FAIL_FLAKE = "flake"

_SINGLE_FAIL_POLICIES = (
    SINGLE_FAIL_UNDETERMINED,
    SINGLE_FAIL_GENUINE,
    SINGLE_FAIL_FLAKE,
)


@dataclass(frozen=True)
class Classification:
    test_id: str
    commit: str
    label: str
    attempt_count: int
    passes: int
    failures: int
    skips: int
    reason: str


def classify_one(
    record: TestOnCommit,
    single_fail_policy: str = SINGLE_FAIL_UNDETERMINED,
) -> Classification:
    passes = record.passes
    failures = record.failures
    skips = record.skips
    n = record.attempt_count

    if failures == 0:
        label = STABLE
        reason = f"all {n} attempt(s) passed or skipped, no failures"
    elif passes > 0 and failures > 0:
        label = FLAKE
        reason = (
            f"same commit produced {passes} pass(es) and {failures} "
            f"failure(s) across {n} attempts"
        )
    elif n == 1:
        # Single attempt, and it failed. Ambiguous by construction.
