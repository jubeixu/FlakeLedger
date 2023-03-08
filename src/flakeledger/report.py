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
    counts: dict[str, int] = {}
    for c in classifications:
        counts[c.label] = counts.get(c.label, 0) + 1
    for label in sorted(counts):
        lines.append(f"count {label} {counts[label]}")
    for c in classifications:
        lines.append(
            f"class {c.test_id} @ {c.commit} {c.label} "
            f"attempts={c.attempt_count} pass={c.passes} "
            f"fail={c.failures} skip={c.skips} ({c.reason})"
        )
    return "\n".join(lines) + "\n"


def render_cost(costs: list[TestCost], rates: Rates, currency: str) -> str:
    lines: list[str] = []
    lines.append("rates:")
    lines.append(
        f"  compute_rate_per_minute {rates.compute_rate_per_minute:.4f} "
        f"{currency}/min"
    )
    lines.append(
        f"  dev_rate_per_minute {rates.dev_rate_per_minute:.4f} {currency}/min"
    )
    lines.append(
        f"  dev_wait_minutes_per_flaky_event "
        f"{rates.dev_wait_minutes_per_flaky_event:.2f} min"
    )
    lines.append("")
    lines.append("ranked flaky test cost (highest first):")

    if not costs:
        lines.append("  none: no test was classified as a flake")
        return "\n".join(lines) + "\n"

    total = 0.0
    for i, c in enumerate(costs, start=1):
        total += c.total_cost
        lines.append(
            f"  {i}. {c.test_id}"
        )
        lines.append(
            f"     events={c.flaky_events} "
            f"wasted_compute={c.wasted_compute_minutes:.3f}min "
            f"dev_wait={c.dev_wait_minutes:.1f}min"
        )
        lines.append(
            f"     compute_cost={c.compute_cost:.4f} {currency} "
            f"dev_cost={c.dev_cost:.4f} {currency} "
            f"total={c.total_cost:.4f} {currency}"
        )
    lines.append("")
    lines.append(f"total flaky cost {total:.4f} {currency}")
# review note
