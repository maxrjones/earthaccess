"""Login exceptions, split out of `earthaccess/exceptions.py`.

Only the two login-related exceptions move — `earthaccess/auth.py` raises
both, so they must live in this package. `DownloadFailure`, `ServiceOutage`,
and `EulaNotAccepted` belong to the download stack and stay in earthaccess
(which re-exports these two from here so `earthaccess.exceptions` keeps its
full surface; see MIGRATION.md).

Complete as written; bodies are verbatim from main.
"""


class LoginStrategyUnavailable(Exception):  # noqa: N818
    """The selected login strategy was skipped.

    This should be raised when a login strategy can't be attempted, for example because
    "environment" was selected but the envvars are not populated.

    DO NOT raise this exception when a login strategy is attempted and fails. For
    example, this exception would not be thrown when credentials were rejected;
    a `LoginAttemptFailure` should be thrown instead.
    """


class LoginAttemptFailure(Exception):  # noqa: N818
    """The login attempt failed.

    This should be raised when a login attempt fails, for example, because
    the user's credentials were rejected.

    DO NOT raise this exception when a login strategy can't be attempted. For
    example, this exception would not be thrown when "environment" was selected
    but the envvars are not populated; a `LoginStrategyUnavailable` should be
    thrown instead.
    """
