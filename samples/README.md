# Sample fixtures

These JUnit XML files are hand authored test vectors, not captured from a real
CI system. They are constructed to exercise every classification path with
known, checkable outcomes. Do not treat them as production data.

Each file is one CI run: one commit at one rerun attempt. The `commit` and
`attempt` values are set either as attributes on the `testsuite` element or as
`<property>` entries inside a `testsuites` wrapper, which is how the parser
reads run identity.

## What each fixture proves

- `run-a1b2c3-attempt1.xml` and `run-a1b2c3-attempt2.xml`
  Commit a1b2c3, run twice. `test_apply_coupon` fails on attempt 1 and passes
  on attempt 2: a flake, because the code did not change between attempts.
  `test_pdf_header` fails on both attempts: a genuine failure.

- `run-d4e5f6-attempt1.xml` and `run-d4e5f6-attempt2.xml`
  Commit d4e5f6, run twice. Same pattern: `test_apply_coupon` flakes again
  (its second flaky event), `test_pdf_header` fails on both attempts again.

- `run-b7c8d9-attempt1.xml` and `run-b7c8d9-attempt2.xml`
  Commit b7c8d9, run twice. `test_replica_catchup` fails then passes: a flake.
  Its runtime is roughly 4.5s, much longer than the coupon test, which is why
  it dominates the wasted compute figure.

- `run-99aa88-attempt1.xml`
