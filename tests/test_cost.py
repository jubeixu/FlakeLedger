import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from flakeledger.classify import classify_all
from flakeledger.cost import Rates, cost_for_flaky_tests
from flakeledger.junit import parse_paths
from flakeledger.runs import group_by_test_commit
from flakeledger import cli

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def _records():
    files = sorted(str(p) for p in SAMPLES.glob("*.xml"))
    results, _ = parse_paths(files)
    return group_by_test_commit(results)


class TestCostModel(unittest.TestCase):
    def setUp(self):
        self.records = _records()
        self.classifications = classify_all(self.records)

    def test_only_flaky_tests_are_charged(self):
        costs = cost_for_flaky_tests(
            self.records, self.classifications, Rates()
        )
        ids = {c.test_id for c in costs}
        self.assertEqual(
            ids,
            {
                "tests.payments.test_checkout.test_apply_coupon",
                "tests.integration.test_sync.test_replica_catchup",
            },
        )

    def test_coupon_cost_matches_hand_calc(self):
