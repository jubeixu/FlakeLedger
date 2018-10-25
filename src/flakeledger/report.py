"""Line oriented, deterministic report rendering.

Output is plain text, one record per line where possible, so results diff
cleanly in git. Currency figures are rounded to a fixed number of places.
"""

from __future__ import annotations

from flakeledger.classify import Classification
from flakeledger.cost import Rates, TestCost
from flakeledger.junit import CaseResult
from flakeledger.runs import TestOnCommit


def render_ingest(results: list[CaseResult], warnings: list[str]) -> str:
    lines: list[str] = []
    lines.append(f"cases {len(results)}")
    commits = sorted({r.commit for r in results})
