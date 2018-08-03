"""The cost model for flaky tests.

Every rate here is an input, not a fact. Defaults are stated so a run
produces numbers, but the defaults are placeholders for your own measured
values, not universal truths. The README documents each assumption.

Two costs are attributed to a flaky test:

  Wasted compute minutes
    A flake causes reruns that would not have happened if the test were
    reliable. We count the extra attempts beyond the first as wasted, and
