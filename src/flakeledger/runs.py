"""Group parsed case results by commit and by test.

The unit of classification is (test_id, commit): the set of outcomes a single
test produced across every rerun attempt of one commit. If a commit was run
three times, a test has up to three attempt records here.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from flakeledger.junit import FAILED, PASSED, SKIPPED, CaseResult


@dataclass
class TestOnCommit:
    """All attempts of one test against one commit."""

    test_id: str
    commit: str
    attempts: list[CaseResult] = field(default_factory=list)

    @property
