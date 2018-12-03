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
        self.by_key = {
            (c.test_id, c.commit): c for c in classify_all(self.records)
        }

    def test_flake_detected(self):
        c = self.by_key[
            ("tests.payments.test_checkout.test_apply_coupon", "a1b2c3")
        ]
        self.assertEqual(c.label, FLAKE)

    def test_genuine_failure_detected(self):
        c = self.by_key[
            ("tests.reports.test_export.test_pdf_header", "a1b2c3")
        ]
        self.assertEqual(c.label, GENUINE_FAILURE)

    def test_stable_detected(self):
        c = self.by_key[
            ("tests.auth.test_login.test_valid_password", "a1b2c3")
        ]
        self.assertEqual(c.label, STABLE)

    def test_second_flaky_test_detected(self):
        c = self.by_key[
            ("tests.integration.test_sync.test_replica_catchup", "b7c8d9")
        ]
        self.assertEqual(c.label, FLAKE)

    def _single_fail_record(self):
        case = CaseResult(
            commit="zz9999",
