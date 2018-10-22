"""Line oriented, deterministic report rendering.

Output is plain text, one record per line where possible, so results diff
cleanly in git. Currency figures are rounded to a fixed number of places.
"""

from __future__ import annotations

from flakeledger.classify import Classification
