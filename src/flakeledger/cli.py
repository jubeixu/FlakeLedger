"""Command line interface for flakeledger.

Subcommands:
  ingest    parse JUnit XML files and list the case results
  classify  label each test on each commit: flake, genuine, stable, undetermined
  cost      rank flaky tests by attributed cost using explicit rates
  version   print the version

Exit codes:
  0  clean, no findings
  1  findings present (a flake or genuine failure was found)
  2  usage error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flakeledger import __version__
from flakeledger import report
from flakeledger.classify import (
    FLAKE,
    GENUINE_FAILURE,
    SINGLE_FAIL_GENUINE,
    SINGLE_FAIL_FLAKE,
    SINGLE_FAIL_UNDETERMINED,
    UNDETERMINED,
    classify_all,
)
from flakeledger.cost import (
    DEFAULT_COMPUTE_RATE_PER_MINUTE,
    DEFAULT_DEV_RATE_PER_MINUTE,
    DEFAULT_DEV_WAIT_MINUTES_PER_FLAKY_EVENT,
    Rates,
    cost_for_flaky_tests,
)
from flakeledger.junit import parse_paths
from flakeledger.runs import group_by_test_commit

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2


def _collect_xml(paths: list[str]) -> list[Path]:
    """Expand each path: a directory yields its *.xml files, a file is itself."""

    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            out.extend(sorted(p.glob("*.xml")))
        elif p.is_file():
            out.append(p)
        # Nonexistent paths are ignored here; the caller reports the empty set
        # as a usage error rather than crashing on a missing file.
    return out


def _add_input_arg(sub: argparse.ArgumentParser) -> None:
    sub.add_argument(
        "inputs",
        nargs="+",
        help="JUnit XML files or directories containing them",
    )


def _add_policy_arg(sub: argparse.ArgumentParser) -> None:
    sub.add_argument(
        "--single-fail-policy",
        choices=[
            SINGLE_FAIL_UNDETERMINED,
            SINGLE_FAIL_GENUINE,
            SINGLE_FAIL_FLAKE,
        ],
        default=SINGLE_FAIL_UNDETERMINED,
        help=(
            "how to label a test that failed on its only attempt for a "
            "commit (default: undetermined, which refuses to guess)"
        ),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flakeledger",
        description="Quantify the cost of flaky tests from JUnit XML results.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="parse JUnit XML and list cases")
    _add_input_arg(p_ingest)

    p_classify = sub.add_parser(
        "classify", help="label tests as flake, genuine, stable, undetermined"
    )
    _add_input_arg(p_classify)
    _add_policy_arg(p_classify)

    p_cost = sub.add_parser("cost", help="rank flaky tests by attributed cost")
    _add_input_arg(p_cost)
    _add_policy_arg(p_cost)
    p_cost.add_argument(
        "--compute-rate-per-minute",
        type=float,
        default=DEFAULT_COMPUTE_RATE_PER_MINUTE,
        help=(
            "cost of one compute minute of CI, in the chosen currency "
            f"(default {DEFAULT_COMPUTE_RATE_PER_MINUTE}, a placeholder)"
        ),
    )
    p_cost.add_argument(
        "--dev-rate-per-minute",
        type=float,
        default=DEFAULT_DEV_RATE_PER_MINUTE,
        help=(
            "cost of one developer minute, in the chosen currency "
            f"(default {DEFAULT_DEV_RATE_PER_MINUTE}, a placeholder)"
        ),
    )
    p_cost.add_argument(
        "--dev-wait-minutes-per-flaky-event",
        type=float,
        default=DEFAULT_DEV_WAIT_MINUTES_PER_FLAKY_EVENT,
        help=(
            "developer minutes lost per flaky event "
            f"(default {DEFAULT_DEV_WAIT_MINUTES_PER_FLAKY_EVENT}, a placeholder)"
        ),
    )
    p_cost.add_argument(
        "--currency",
        default="USD",
        help="currency label to print next to figures (default USD)",
    )

    sub.add_parser("version", help="print the version and exit")
    return parser


def _load(inputs: list[str]):
    files = _collect_xml(inputs)
    if not files:
        return None, None, "no XML files found in the given inputs"
    results, warnings = parse_paths([str(f) for f in files])
    return results, warnings, None


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        sys.stdout.write(f"flakeledger {__version__}\n")
        return EXIT_CLEAN

    results, warnings, err = _load(args.inputs)
    if err is not None:
        sys.stderr.write(f"error: {err}\n")
        return EXIT_USAGE

    if args.command == "ingest":
        sys.stdout.write(report.render_ingest(results, warnings))
        return EXIT_CLEAN

    records = group_by_test_commit(results)

    if args.command == "classify":
        classifications = classify_all(records, args.single_fail_policy)
        sys.stdout.write(
            report.render_classify(classifications, args.single_fail_policy)
        )
        findings = any(
            c.label in (FLAKE, GENUINE_FAILURE, UNDETERMINED)
            for c in classifications
        )
        return EXIT_FINDINGS if findings else EXIT_CLEAN

    if args.command == "cost":
        classifications = classify_all(records, args.single_fail_policy)
        rates = Rates(
            compute_rate_per_minute=args.compute_rate_per_minute,
            dev_rate_per_minute=args.dev_rate_per_minute,
            dev_wait_minutes_per_flaky_event=args.dev_wait_minutes_per_flaky_event,
        )
        costs = cost_for_flaky_tests(records, classifications, rates)
        sys.stdout.write(report.render_cost(costs, rates, args.currency))
        return EXIT_FINDINGS if costs else EXIT_CLEAN

    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
