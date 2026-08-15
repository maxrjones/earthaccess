from earthaccess_auth.exceptions import (
    LoginAttemptFailure,
    LoginStrategyUnavailable,
)


class DownloadFailure(Exception):  # noqa: N818
    """The download attempt failed.

    This should be raised when a download attempt fails, for example, because
    the file could not be retrieved or the download process was interrupted.
    """


class ServiceOutage(Exception):  # noqa: N818
    """A service outage has been detected.

    This should be raised when Earthdata services are unavailable or experiencing
    outages that prevent normal operations.
    """


class EulaNotAccepted(DownloadFailure):
    """The user has not accepted the EULA.

    This should be raised when a user attempts to access data that requires
    EULA acceptance, but they have not accepted the EULA.
    """


__all__ = [
    "DownloadFailure",
    "EulaNotAccepted",
    "LoginAttemptFailure",
    "LoginStrategyUnavailable",
    "ServiceOutage",
]
