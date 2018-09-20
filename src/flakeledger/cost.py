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
