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
