"""Unit tests for the auth core.

SKETCH: `tests/unit/test_auth.py` moves here essentially verbatim — it
already exercises only the extracted surface. The mechanical edits:

- `from earthaccess import Auth` -> `from earthaccess_auth import Auth`
- `from earthaccess.exceptions import LoginAttemptFailure`
  -> `from earthaccess_auth.exceptions import LoginAttemptFailure`

The moved cases (all in TestCreateAuth, using responses + mock stdin/getpass):

- test_auth_gets_proper_credentials
- test_auth_can_create_proper_credentials
- test_auth_can_parse_existing_user_token
- test_auth_fails_for_wrong_credentials

New coverage worth adding here (not on main today):

- module-level `login(strategy="all")` fallback order: environment before
  netrc, LoginStrategyUnavailable skips to the next strategy, first success
  stops the chain.
- adapters import guard: importing `earthaccess_auth` succeeds without
  fsspec/obstore installed (the core-stays-requests-only invariant).

earthaccess keeps a thin `tests/unit/test_auth.py` that imports Auth via
`earthaccess` to pin the re-export shim (see MIGRATION.md).
"""
