"""Classify each test on each commit as a flake, a genuine failure, or stable.

Definitions used here, stated so the label is auditable:

  FLAKE
    The same test, on the same commit, both passed and failed across its
    reruns. The code did not change between attempts, so a differing outcome
    means the test result depends on something other than the code. That is
    the operational definition of a flaky test.

  GENUINE_FAILURE
    Every attempt of the test on that commit failed. The failure reproduces,
