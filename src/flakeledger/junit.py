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
SKIPPED = "skipped"

_UNKNOWN_COMMIT = "unknown-commit"
_DEFAULT_ATTEMPT = 1


@dataclass(frozen=True)
class CaseResult:
    """One test case outcome within one CI run."""

    commit: str
    attempt: int
    suite: str
    classname: str
    name: str
    status: str
    time_seconds: float
    source_file: str

    @property
    def test_id(self) -> str:
        """Stable identifier for a test across runs.

        Combines classname and name. When classname is empty we use the
        name alone. This is what groups reruns of the same test together.
        """

        if self.classname:
            return f"{self.classname}.{self.name}"
        return self.name


def _read_run_metadata(elem: ET.Element) -> tuple[str, int, bool, bool]:
    """Return (commit, attempt, used_default, bad_attempt) from a suite element.

    Reads attributes first, then `<property name=...>` children. Missing
    values fall back to documented defaults and set used_default to True.
    bad_attempt is set when an attempt value is present but not a valid
    integer, so callers can warn about malformed metadata instead of
    silently treating it as absent.
    """

    commit = elem.get("commit")
    attempt_raw = elem.get("attempt")

    if commit is None or attempt_raw is None:
        for prop in elem.iter("property"):
            pname = prop.get("name")
            if pname == "commit" and commit is None:
                commit = prop.get("value")
            elif pname == "attempt" and attempt_raw is None:
                attempt_raw = prop.get("value")

    used_default = False
    bad_attempt = False
    if commit is None:
        commit = _UNKNOWN_COMMIT
        used_default = True
    if attempt_raw is None:
        attempt = _DEFAULT_ATTEMPT
        used_default = True
    else:
        try:
            attempt = int(attempt_raw)
        except ValueError:
            attempt = _DEFAULT_ATTEMPT
            used_default = True
            bad_attempt = True

    return commit, attempt, used_default, bad_attempt


def _case_status(case: ET.Element) -> str:
    for child in case:
        tag = child.tag.lower()
        if tag in ("failure", "error"):
            return FAILED
        if tag == "skipped":
            return SKIPPED
    return PASSED


def _parse_time(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def _iter_suites(root: ET.Element):
    """Yield every testsuite element, whether root is a suite or a suites set."""

    tag = root.tag.lower()
    if tag == "testsuite":
        yield root
    for suite in root.iter("testsuite"):
        yield suite


def parse_file(path: str | Path) -> tuple[list[CaseResult], list[str]]:
    """Parse one JUnit XML file.

    Returns (results, warnings). Warnings are human readable strings, one per
    condition worth surfacing, for example a suite that lacked commit metadata.
    """

    path = Path(path)
    warnings: list[str] = []
    tree = ET.parse(path)
    root = tree.getroot()

    results: list[CaseResult] = []
    seen_suites: set[int] = set()

    for suite in _iter_suites(root):
        marker = id(suite)
        if marker in seen_suites:
            continue
        seen_suites.add(marker)

        commit, attempt, used_default, bad_attempt = _read_run_metadata(suite)
        if used_default:
            commit_r, attempt_r, root_default, root_bad = _read_run_metadata(root)
            if not root_default:
                commit, attempt, used_default = commit_r, attempt_r, False
                bad_attempt = root_bad

        if bad_attempt:
            warnings.append(
                f"{path.name}: suite '{suite.get('name', '')}' has a "
                f"non-integer attempt value, used default {attempt}"
            )
        elif used_default:
            warnings.append(
                f"{path.name}: suite '{suite.get('name', '')}' missing commit "
                f"or attempt metadata, used defaults "
                f"(commit={commit}, attempt={attempt})"
            )

        suite_name = suite.get("name", "")
        for case in suite.findall("testcase"):
            results.append(
                CaseResult(
                    commit=commit,
                    attempt=attempt,
                    suite=suite_name,
                    classname=case.get("classname", ""),
                    name=case.get("name", ""),
                    status=_case_status(case),
                    time_seconds=_parse_time(case.get("time")),
                    source_file=path.name,
                )
            )

    return results, warnings


def parse_paths(paths: list[str | Path]) -> tuple[list[CaseResult], list[str]]:
    """Parse many files, sorted by name for deterministic ordering."""

    ordered = sorted(Path(p) for p in paths)
    all_results: list[CaseResult] = []
    all_warnings: list[str] = []
    for p in ordered:
        results, warnings = parse_file(p)
        all_results.extend(results)
        all_warnings.extend(warnings)
    return all_results, all_warnings
