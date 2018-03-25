"""Parse JUnit XML result files into structured test case records.

The parser uses xml.etree from the standard library. It reads the common
JUnit schema produced by pytest, Gradle, Maven Surefire, and similar tools:
a `testsuites` root (or a single `testsuite`) containing `testcase` elements.

Each `testcase` may carry a child element that marks its outcome:
  - `<failure>` or `<error>`  the test did not pass
  - `<skipped>`               the test was skipped
  - no child element          the test passed

We also read metadata that identifies which CI run a suite belongs to.
Two attributes drive the rest of the pipeline:
  - `commit`   the source revision under test
  - `attempt`  the rerun index for that commit (1 for the first run)

These are read from the `testsuite` (or `testsuites`) element. They are not
part of the base JUnit schema, so a producer must set them as attributes or
as `<property>` entries. When they are absent we fall back to documented
defaults and record that we did so, rather than guessing silently.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

PASSED = "passed"
FAILED = "failed"
