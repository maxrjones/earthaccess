"""EDL authentication: login strategies, token lifecycle, redirect-safe sessions.

SKETCH: every body below moves unchanged from `earthaccess/auth.py` on main
(395 lines), with two mechanical edits:

- imports retarget to `earthaccess_auth.daac`, `earthaccess_auth.exceptions`
  (`LoginAttemptFailure`, `LoginStrategyUnavailable`), and
  `earthaccess_auth.system`;
- the module-level `user_agent` string reads
  `importlib.metadata.version("earthaccess-auth")` instead of `"earthaccess"`,
  so requests from auth-only installs report a version that exists. (Whether
  earthaccess proper should append its own version to the User-Agent is a
  MIGRATION.md note, not this package's concern.)

`typing_extensions.deprecated` (used on `refresh_tokens`) adds a
typing-extensions runtime dependency; it is in pyproject.

Only the surface is spelled out here so reviewers can see what this
distribution exports; `...` marks moved-verbatim implementations.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import requests
from typing_extensions import deprecated

from earthaccess_auth.system import System


def netrc_path() -> Path:
    """Return the netrc file path honoring the NETRC env override, defaulting
    to ~/_netrc on Windows and ~/.netrc elsewhere."""
    ...


class BasicAuthResponseHook:
    """Response hook applying HTTP basic auth only to the EDL hostname."""

    def __init__(self, hostname: str, auth: tuple[str, str]) -> None: ...

    def __call__(self, r: requests.Response, **kwargs: Any) -> requests.Response: ...


class SessionWithHeaderRedirection(requests.Session):
    """Session that keeps the Authorization header across EDL redirects while
    stripping it on redirects to any other host."""

    def __init__(self, edl_hostname: str, auth: tuple[str, str] | None = None) -> None: ...


class Auth:
    """EDL authentication state: credentials, user token, session factories.

    `token` is the raw EDL token mapping (at minimum `access_token`; when
    minted via username/password it also carries `expiration_date`). The
    formalized-token-surface open question in the README would grow the API
    here.
    """

    authenticated: bool
    token: Mapping[str, str] | None
    system: System

    def __init__(self) -> None: ...

    def login(
        self,
        strategy: str = "netrc",
        persist: bool = False,
        system: System | None = None,
    ) -> "Auth":
        """Authenticate via a single strategy: "interactive", "netrc", or
        "environment".

        The "all" fallback chain is NOT here — on main it lives in
        `earthaccess.api.login`, and in this package it lives in the
        module-level `earthaccess_auth.login` (see __init__.py). Raises
        LoginStrategyUnavailable / LoginAttemptFailure as on main.
        """
        ...

    @deprecated("No replacement, as tokens are now refreshed automatically.")
    def refresh_tokens(self) -> bool:
        """Deprecated no-op retained for drop-in compatibility; returns
        `self.authenticated`."""
        ...

    def get_s3_credentials(
        self,
        daac: str | None = None,
        provider: str | None = None,
        endpoint: str | None = None,
    ) -> dict[str, str]:
        """Exchange the EDL session for temporary S3 credentials from a DAAC
        endpoint (looked up in the DAAC registry unless given explicitly).
        Returns {} when unauthenticated or when the exchange fails."""
        ...

    def get_session(self) -> requests.Session:
        """Return a SessionWithHeaderRedirection carrying the bearer token header."""
        ...

    # Private strategy/persistence helpers move along unchanged:
    # _set_earthdata_system, _interactive, _netrc, _environment,
    # _get_credentials, _find_or_create_token, _persist_user_credentials,
    # _get_cloud_auth_url
