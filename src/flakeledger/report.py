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
    lines.append(f"commits {len(commits)}")
    for c in commits:
        lines.append(f"commit {c}")
    for r in sorted(results, key=lambda x: (x.commit, x.attempt, x.test_id)):
        lines.append(
            f"case {r.commit} attempt={r.attempt} {r.test_id} "
            f"{r.status} time={r.time_seconds:.3f}s"
        )
    for w in warnings:
        lines.append(f"warning {w}")
    return "\n".join(lines) + "\n"


def render_classify(
    classifications: list[Classification], policy: str
) -> str:
    lines: list[str] = []
    lines.append(f"policy single_fail={policy}")
