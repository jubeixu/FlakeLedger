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
