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
        # coupon flaked on a1b2c3 (mean time of 0.812 and 0.788 = 0.800s) and
        # d4e5f6 (0.905 and 0.842 = 0.8735s). Each commit had 2 attempts, so
        # 1 extra attempt each. Wasted minutes = mean/60 * 1.
        rates = Rates(
            compute_rate_per_minute=0.01,
            dev_rate_per_minute=1.0,
            dev_wait_minutes_per_flaky_event=10.0,
        )
        costs = cost_for_flaky_tests(self.records, self.classifications, rates)
        coupon = next(
            c
            for c in costs
            if c.test_id == "tests.payments.test_checkout.test_apply_coupon"
        )
        expected_wasted = (0.800 / 60.0) + (0.8735 / 60.0)
        self.assertEqual(coupon.flaky_events, 2)
        self.assertAlmostEqual(
            coupon.wasted_compute_minutes, expected_wasted, places=6
        )
        self.assertAlmostEqual(coupon.dev_wait_minutes, 20.0, places=6)
        self.assertAlmostEqual(
            coupon.compute_cost, expected_wasted * 0.01, places=6
        )
        self.assertAlmostEqual(coupon.dev_cost, 20.0 * 1.0, places=6)

    def test_ranking_descending_by_total(self):
        costs = cost_for_flaky_tests(
            self.records, self.classifications, Rates()
        )
