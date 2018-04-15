"""Group parsed case results by commit and by test.

The unit of classification is (test_id, commit): the set of outcomes a single
test produced across every rerun attempt of one commit. If a commit was run
three times, a test has up to three attempt records here.
"""

from __future__ import annotations
