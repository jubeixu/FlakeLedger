import unittest
from pathlib import Path

from flakeledger.classify import (
    FLAKE,
    GENUINE_FAILURE,
    STABLE,
    UNDETERMINED,
    SINGLE_FAIL_FLAKE,
    SINGLE_FAIL_GENUINE,
    SINGLE_FAIL_UNDETERMINED,
    classify_all,
    classify_one,
)
from flakeledger.junit import parse_paths
from flakeledger.runs import group_by_test_commit, TestOnCommit
from flakeledger.junit import CaseResult

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def _all_records():
    files = sorted(str(p) for p in SAMPLES.glob("*.xml"))
    results, _ = parse_paths(files)
    return group_by_test_commit(results)


class TestClassification(unittest.TestCase):
    def setUp(self):
        self.records = _all_records()
