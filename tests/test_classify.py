import unittest
from pathlib import Path

from flakeledger.classify import (
    FLAKE,
    GENUINE_FAILURE,
    STABLE,
    UNDETERMINED,
    SINGLE_FAIL_FLAKE,
    SINGLE_FAIL_GENUINE,
