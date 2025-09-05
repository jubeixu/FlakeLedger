import unittest
from pathlib import Path

from flakeledger.junit import FAILED, PASSED, parse_file, parse_paths

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


class TestJunitParsing(unittest.TestCase):
    def test_parses_attribute_metadata(self):
        results, warnings = parse_file(SAMPLES / "run-a1b2c3-attempt1.xml")
        self.assertEqual(warnings, [])
        self.assertEqual(len(results), 4)
        commits = {r.commit for r in results}
        self.assertEqual(commits, {"a1b2c3"})
        self.assertTrue(all(r.attempt == 1 for r in results))

    def test_status_detection(self):
        results, _ = parse_file(SAMPLES / "run-a1b2c3-attempt1.xml")
        by_id = {r.test_id: r for r in results}
        self.assertEqual(
            by_id["tests.payments.test_checkout.test_apply_coupon"].status,
            FAILED,
        )
        self.assertEqual(
            by_id["tests.payments.test_checkout.test_total_with_tax"].status,
            PASSED,
        )

    def test_reads_property_metadata_in_testsuites_wrapper(self):
        results, warnings = parse_file(SAMPLES / "run-99aa88-attempt1.xml")
        self.assertEqual(warnings, [])
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.commit == "99aa88" for r in results))
        self.assertTrue(all(r.attempt == 1 for r in results))

    def test_time_parsing(self):
        results, _ = parse_file(SAMPLES / "run-a1b2c3-attempt1.xml")
        header = next(
            r
            for r in results
            if r.name == "test_pdf_header"
        )
        self.assertAlmostEqual(header.time_seconds, 1.930, places=3)

    def test_parse_paths_is_sorted_and_complete(self):
        files = sorted(str(p) for p in SAMPLES.glob("*.xml"))
        results, _ = parse_paths(files)
        # a1b2c3: 4 + 4, d4e5f6: 4 + 4, b7c8d9: 3 + 3, 99aa88: 3 = 25 rows.
        self.assertEqual(len(results), 25)


if __name__ == "__main__":
    unittest.main()
