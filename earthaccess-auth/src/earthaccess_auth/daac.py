"""DAAC registry and provider lookup.

SKETCH: moves verbatim from `earthaccess/daac.py` (159 lines): the DAACS
table (cloud providers, on-prem providers, S3 credential endpoints) and its
lookup helpers. No changes needed; it already depends on nothing.
"""

DAACS: list[dict] = ...  # type: ignore[assignment]
