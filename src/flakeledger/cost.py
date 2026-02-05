"""The cost model for flaky tests.

Every rate here is an input, not a fact. Defaults are stated so a run
produces numbers, but the defaults are placeholders for your own measured
values, not universal truths. The README documents each assumption.

Two costs are attributed to a flaky test:

  Wasted compute minutes
    A flake causes reruns that would not have happened if the test were
    reliable. We count the extra attempts beyond the first as wasted, and
    multiply the flaky test's mean runtime by the number of extra attempts,
    then convert to a money figure with `compute_rate_per_minute`.

    This is a lower bound. In real CI a single flaky test usually forces a
    rerun of an entire job, not just itself, so the true compute waste is
    larger. We deliberately attribute only the test's own time because that
    is the part we can measure from the JUnit data without guessing job
    composition. This limitation is stated in the README.

  Developer wait cost
    A red pipeline blocks the developer who is waiting on it. We model this
    as `dev_wait_minutes_per_flaky_event` minutes of human time per flaky
    event (one event per commit where the test flaked), valued at
    `dev_rate_per_minute`. Both numbers are inputs.

All rates carry units in their names. Nothing is hardcoded inside the
formula: change the rates and every number moves.
"""

from __future__ import annotations

from dataclasses import dataclass

from flakeledger.classify import FLAKE, Classification
from flakeledger.runs import TestOnCommit

# Documented default rates. These are placeholders, not measurements.
# Sources for your own values: CI invoice divided by billed minutes for the
# compute rate, and loaded engineering cost per minute for the developer rate.
DEFAULT_COMPUTE_RATE_PER_MINUTE = 0.008  # currency units per compute minute
DEFAULT_DEV_RATE_PER_MINUTE = 1.50  # currency units per developer minute
DEFAULT_DEV_WAIT_MINUTES_PER_FLAKY_EVENT = 15.0  # minutes lost per flaky event


@dataclass(frozen=True)
class Rates:
    compute_rate_per_minute: float = DEFAULT_COMPUTE_RATE_PER_MINUTE
    dev_rate_per_minute: float = DEFAULT_DEV_RATE_PER_MINUTE
    dev_wait_minutes_per_flaky_event: float = DEFAULT_DEV_WAIT_MINUTES_PER_FLAKY_EVENT


@dataclass(frozen=True)
class TestCost:
    test_id: str
    flaky_events: int
    wasted_compute_minutes: float
    dev_wait_minutes: float
    compute_cost: float
    dev_cost: float

    @property
    def total_cost(self) -> float:
        return self.compute_cost + self.dev_cost


def _extra_attempts(record: TestOnCommit) -> int:
    # Attempts beyond the first are reruns that a reliable test would avoid.
    return max(record.attempt_count - 1, 0)


def cost_for_flaky_tests(
    records: list[TestOnCommit],
    classifications: list[Classification],
    rates: Rates,
) -> list[TestCost]:
    """Compute per-test cost, aggregated across every commit where it flaked.

    Only tests classified FLAKE on at least one commit are charged. Output is
    ranked by total cost descending, ties broken by test_id for determinism.
    """

    flake_keys = {
        (c.test_id, c.commit) for c in classifications if c.label == FLAKE
    }
    record_by_key = {(r.test_id, r.commit): r for r in records}

    agg: dict[str, dict[str, float]] = {}
    for (test_id, commit) in sorted(flake_keys):
        record = record_by_key[(test_id, commit)]
        extra = _extra_attempts(record)
        wasted_minutes = (record.mean_time_seconds / 60.0) * extra

        slot = agg.setdefault(
            test_id,
            {"events": 0.0, "wasted_minutes": 0.0, "dev_minutes": 0.0},
        )
        slot["events"] += 1
        slot["wasted_minutes"] += wasted_minutes
        slot["dev_minutes"] += rates.dev_wait_minutes_per_flaky_event

    costs: list[TestCost] = []
    for test_id, slot in agg.items():
        compute_cost = slot["wasted_minutes"] * rates.compute_rate_per_minute
        dev_cost = slot["dev_minutes"] * rates.dev_rate_per_minute
        costs.append(
            TestCost(
                test_id=test_id,
                flaky_events=int(slot["events"]),
                wasted_compute_minutes=slot["wasted_minutes"],
                dev_wait_minutes=slot["dev_minutes"],
                compute_cost=compute_cost,
                dev_cost=dev_cost,
            )
        )

    costs.sort(key=lambda c: (-round(c.total_cost, 6), c.test_id))
    return costs
