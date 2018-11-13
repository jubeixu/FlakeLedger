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
