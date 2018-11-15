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

